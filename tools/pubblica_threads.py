#!/usr/bin/env python3
"""Pubblicatore Threads: prende dalla coda le voci tipo="threads" scadute e le pubblica.

Sicurezza per costruzione
-------------------------
Il DRY-RUN E' IL DEFAULT. Senza il flag esplicito `--vai` il programma non tocca la rete
e non scrive nulla: stampa soltanto cosa uscirebbe. Un errore di lancio non puo' quindi
sparare post veri.

La rete passa da UN SOLO punto: la funzione `_http_post()` (piu' `_http_get()` per il
permalink). Tutto il resto e' logica pura e gira ovunque.

Come si lancia DAVVERO (produzione)
-----------------------------------
Il container NON ha rete verso graph.threads.net: dal container si puo' fare solo il
dry-run. La pubblicazione vera si fa su una macchina con rete, cioe' via
`COMPOSIO_REMOTE_BASH_TOOL`. Procedura, tre comandi:

1) DAL CONTAINER — controllo di cosa uscirebbe (nessuna rete, nessuna scrittura):

       python3 tools/pubblica_threads.py

2) SU COMPOSIO — si portano su la coda e questo file, poi si pubblica davvero:

       curl -s -o queue.json https://raw.githubusercontent.com/Cerbero99-bombon/accumunation-media/main/queue.json
       curl -s -o pubblica_threads.py https://raw.githubusercontent.com/Cerbero99-bombon/accumunation-media/main/tools/pubblica_threads.py
       THREADS_TOKEN='...' THREADS_USER_ID='27480059418283747' \
         python3 pubblica_threads.py --vai --coda queue.json
       cat queue.json   # <-- la coda aggiornata, con pubblicato=true e i permalink

   (in alternativa al token da ambiente: `--token ...`; l'ambiente e' preferibile,
   cosi' il token non finisce nei log dei comandi)

3) DAL CONTAINER — si riporta la coda aggiornata nel repo e si committa
   (`Cerbero99-bombon` / `01enricodesimini99@gmail.com`).

ATTENZIONE alla finestra di silenzio 19:00-23:00 Roma di CAMBIAMENTI.md: in quella
fascia lavora il pubblicatore Instagram e `queue.json` non si tocca a mano.

Regole rispettate (le stesse del pubblicatore IG, vedi tools/controllo_coda.py)
------------------------------------------------------------------------------
- si pubblica solo `pubblicato=false` con `quando` gia' arrivata (ora di Roma);
- una voce NON pubblicata non porta mai il campo `permalink`: viene scritto solo
  insieme a `pubblicato=true`, mai prima;
- massimo 3 uscite per run (`--max`), come da "nota" della coda;
- la coda viene riscritta su disco DOPO OGNI singola pubblicazione riuscita: se il run
  muore a meta', quello che e' gia' uscito risulta gia' marcato e non esce due volte;
- se la creazione del contenitore fallisce, `pubblicato` NON viene toccato;
- se fallisce la publish DOPO che il contenitore esiste, il `creation_id` viene stampato
  e salvato nel report: non si perde e si puo' ripubblicare a mano con
  `--pubblica-creation-id <id>`.

Uscita: 0 se tutto bene (anche a coda vuota), 1 se almeno una voce e' fallita.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import urllib.parse

API = "https://graph.threads.net/v1.0"
TIPO = "threads"
MAX_DEFAULT = 3
MAX_CARATTERI = 500  # limite di un post Threads di testo


class ErroreThreads(Exception):
    """Qualunque cosa vada storta parlando con l'API."""


# ---------------------------------------------------------------- rete (unico punto)

def _curl(url, campi, metodo):
    """L'UNICO posto del file da cui esce traffico di rete.

    Usa curl perche' e' presente ovunque (container e macchina Composio) e non
    richiede pacchetti python. Ritorna il JSON di risposta gia' decodificato.
    """
    cmd = ["curl", "-sS", "-X", metodo, "-w", "\n%{http_code}", "--max-time", "60"]
    if metodo == "POST":
        cmd += ["-d", urllib.parse.urlencode(campi)]
        cmd += [url]
    else:
        cmd += [url + "?" + urllib.parse.urlencode(campi)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        raise ErroreThreads("timeout della richiesta (90s)")
    if r.returncode != 0:
        raise ErroreThreads(f"curl fallito ({r.returncode}): {r.stderr.strip()[:300]}")
    testo, _, codice = r.stdout.rpartition("\n")
    try:
        dati = json.loads(testo) if testo.strip() else {}
    except json.JSONDecodeError:
        raise ErroreThreads(f"risposta non JSON (HTTP {codice}): {testo.strip()[:300]}")
    if codice != "200" or "error" in dati:
        err = dati.get("error", {})
        raise ErroreThreads(
            f"HTTP {codice} · {err.get('type', '?')} {err.get('code', '?')}: "
            f"{err.get('message', testo.strip()[:300])}"
        )
    return dati


def _http_post(url, campi):
    return _curl(url, campi, "POST")


def _http_get(url, campi):
    return _curl(url, campi, "GET")


# ------------------------------------------------------------------ passi dell'API

def crea_contenitore(user_id, token, testo):
    """Passo 1: crea il contenitore. Ritorna il creation_id."""
    dati = _http_post(f"{API}/{user_id}/threads",
                      {"media_type": "TEXT", "text": testo, "access_token": token})
    cid = dati.get("id")
    if not cid:
        raise ErroreThreads(f"nessun id nella risposta di creazione: {dati}")
    return cid


def pubblica_contenitore(user_id, token, creation_id):
    """Passo 2: pubblica il contenitore. Ritorna l'id del media pubblicato."""
    dati = _http_post(f"{API}/{user_id}/threads_publish",
                      {"creation_id": creation_id, "access_token": token})
    mid = dati.get("id")
    if not mid:
        raise ErroreThreads(f"nessun id nella risposta di publish: {dati}")
    return mid


def leggi_permalink(media_id, token, tentativi=3):
    """Passo 3: il permalink del post appena uscito. None se non si riesce a leggerlo.

    NON e' un fallimento della pubblicazione: a questo punto il post e' gia' fuori.
    """
    ultimo = None
    for _ in range(tentativi):
        try:
            return _http_get(f"{API}/{media_id}", {"fields": "permalink", "access_token": token})["permalink"]
        except (ErroreThreads, KeyError) as e:
            ultimo = e
    print(f"    [avviso] permalink non recuperato ({ultimo}); media_id={media_id}")
    return None


# ------------------------------------------------------------------------ la coda

def carica_coda(percorso):
    with open(percorso, encoding="utf-8") as f:
        return json.load(f)


def salva_coda(percorso, coda):
    """Stesso identico formato del file in repo: indent=1, utf-8, senza newline finale."""
    tmp = percorso + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(coda, ensure_ascii=False, indent=1))
    os.replace(tmp, percorso)


def adesso_roma():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("Europe/Rome")).replace(tzinfo=None)
    except Exception:
        # senza tzdata: ora legale europea (ultima domenica di marzo -> ultima di ottobre)
        u = datetime.datetime.utcnow()
        def ultima_domenica(mese):
            g = datetime.datetime(u.year, mese, 31, 1)
            return g - datetime.timedelta(days=(g.weekday() + 1) % 7)
        legale = ultima_domenica(3) <= u < ultima_domenica(10)
        return u + datetime.timedelta(hours=2 if legale else 1)


def quando_a_data(voce):
    """"2026-08-05 20:00 Roma" -> datetime naive in ora di Roma."""
    grezzo = str(voce.get("quando", "")).replace(" Roma", "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(grezzo, fmt)
        except ValueError:
            continue
    raise ErroreThreads(f"campo 'quando' illeggibile: {voce.get('quando')!r}")


def testo_della_voce(voce):
    """Il testo che finisce su Threads: `testo`, altrimenti `caption`, altrimenti `titolo`."""
    for chiave in ("testo", "caption", "titolo"):
        v = voce.get(chiave)
        if v and str(v).strip():
            return str(v).strip()
    return None


def da_pubblicare(coda, adesso, massimo):
    """Le voci threads mature, in ordine di `quando`. Le scartate escono come avvisi."""
    buone, scarti = [], []
    for voce in coda.get("post", []):
        if voce.get("tipo") != TIPO:
            continue
        pid = voce.get("id") or voce.get("titolo") or "???"
        if voce.get("pubblicato"):
            continue  # gia' uscita: mai una seconda volta
        if voce.get("permalink"):
            # incoerenza: non pubblicata ma con permalink. Non si tocca, si segnala.
            scarti.append((pid, "non pubblicata ma HA gia' un permalink — voce sospetta, salto"))
            continue
        try:
            quando = quando_a_data(voce)
        except ErroreThreads as e:
            scarti.append((pid, str(e)))
            continue
        if quando > adesso:
            continue  # non e' ancora ora
        testo = testo_della_voce(voce)
        if not testo:
            scarti.append((pid, "nessun testo (ne' 'testo' ne' 'caption' ne' 'titolo')"))
            continue
        if len(testo) > MAX_CARATTERI:
            scarti.append((pid, f"testo di {len(testo)} caratteri, oltre il limite di {MAX_CARATTERI}"))
            continue
        buone.append((quando, pid, voce, testo))
    buone.sort(key=lambda t: t[0])
    troppe = buone[massimo:]
    for _, pid, _, _ in troppe:
        scarti.append((pid, f"oltre il tetto di {massimo} per run — rimandata al prossimo giro"))
    return buone[:massimo], scarti


# ------------------------------------------------------------------------- il run

def esegui(coda, percorso, voci, token, user_id, vai):
    esiti = []
    for quando, pid, voce, testo in voci:
        print(f"\n  · {pid}  ({voce.get('quando')})")
        for riga in testo.splitlines() or [""]:
            print(f"      | {riga}")
        print(f"      [{len(testo)} caratteri]")
        if not vai:
            esiti.append({"id": pid, "esito": "dry-run"})
            continue

        # --- passo 1: contenitore. Se fallisce, `pubblicato` NON si tocca.
        try:
            creation_id = crea_contenitore(user_id, token, testo)
        except ErroreThreads as e:
            print(f"    [ERRORE] creazione contenitore fallita: {e}")
            print("    -> voce NON marcata, riprovera' al prossimo run")
            esiti.append({"id": pid, "esito": "errore-creazione", "dettaglio": str(e)})
            continue
        print(f"    contenitore creato: creation_id={creation_id}")

        # --- passo 2: publish. Se fallisce QUI il creation_id non deve andare perso.
        try:
            media_id = pubblica_contenitore(user_id, token, creation_id)
        except ErroreThreads as e:
            print(f"    [ERRORE] publish fallita: {e}")
            print(f"    -> CREATION_ID DA NON PERDERE: {creation_id}")
            print(f"       ripubblicabile con: python3 {os.path.basename(__file__)} "
                  f"--pubblica-creation-id {creation_id} --vai")
            print("    -> voce NON marcata (il post non risulta uscito)")
            esiti.append({"id": pid, "esito": "errore-publish",
                          "creation_id": creation_id, "dettaglio": str(e)})
            continue
        print(f"    PUBBLICATO: media_id={media_id}")

        # --- passo 3: permalink e marcatura. Da qui in poi il post E' FUORI.
        permalink = leggi_permalink(media_id, token)
        voce["pubblicato"] = True
        voce["threads_media_id"] = media_id
        if permalink:
            voce["permalink"] = permalink
            print(f"    permalink: {permalink}")
        else:
            print("    [avviso] permalink assente: controllo_coda.py lo segnalera'. "
                  "Va messo a mano dal media_id qui sopra.")
        # si salva SUBITO: un crash dopo questa riga non fa uscire nulla due volte
        salva_coda(percorso, coda)
        print(f"    coda aggiornata su {percorso}")
        esiti.append({"id": pid, "esito": "pubblicato",
                      "media_id": media_id, "permalink": permalink})
    return esiti


def main():
    ap = argparse.ArgumentParser(
        description="Pubblica su Threads le voci tipo=threads della coda. Default: dry-run.")
    ap.add_argument("--vai", action="store_true",
                    help="PUBBLICA DAVVERO. Senza questo flag e' sempre e solo dry-run.")
    ap.add_argument("--dry-run", action="store_true",
                    help="esplicito, ma e' gia' il comportamento di default")
    ap.add_argument("--coda", default="queue.json", help="percorso di queue.json")
    ap.add_argument("--max", type=int, default=MAX_DEFAULT,
                    help=f"tetto di uscite per run (default {MAX_DEFAULT})")
    ap.add_argument("--token", default=os.environ.get("THREADS_TOKEN"),
                    help="access token; meglio via variabile d'ambiente THREADS_TOKEN")
    ap.add_argument("--user-id", default=os.environ.get("THREADS_USER_ID", "27480059418283747"))
    ap.add_argument("--adesso", help="finge un'altra ora di Roma, formato 'YYYY-MM-DD HH:MM' (per collaudo)")
    ap.add_argument("--pubblica-creation-id",
                    help="recupero: pubblica un contenitore gia' creato e stampa il permalink. "
                         "La coda NON viene toccata: il permalink si scrive a mano.")
    ap.add_argument("--report", help="scrive l'esito del run in questo file JSON")
    args = ap.parse_args()

    vai = args.vai and not args.dry_run
    if args.dry_run and args.vai:
        print("[!] --dry-run e --vai insieme: vince la prudenza, nessuna pubblicazione.")

    if args.pubblica_creation_id:
        if not vai:
            print(f"DRY-RUN: pubblicherei il contenitore {args.pubblica_creation_id}. "
                  "Aggiungi --vai per farlo davvero.")
            return 0
        if not args.token:
            print("[ERRORE] manca il token (THREADS_TOKEN o --token)"); return 1
        try:
            mid = pubblica_contenitore(args.user_id, args.token, args.pubblica_creation_id)
        except ErroreThreads as e:
            print(f"[ERRORE] publish fallita: {e}"); return 1
        print(f"PUBBLICATO: media_id={mid} · permalink={leggi_permalink(mid, args.token)}")
        print("Ricorda: scrivi a mano pubblicato=true e il permalink nella coda.")
        return 0

    adesso = (datetime.datetime.strptime(args.adesso, "%Y-%m-%d %H:%M")
              if args.adesso else adesso_roma())
    coda = carica_coda(args.coda)
    voci, scarti = da_pubblicare(coda, adesso, args.max)

    modo = "PUBBLICAZIONE VERA" if vai else "DRY-RUN (nessuna rete, nessuna scrittura)"
    print(f"=== pubblica_threads · {modo} ===")
    print(f"ora di Roma: {adesso:%Y-%m-%d %H:%M} · coda: {args.coda} · tetto: {args.max}")
    totali = [p for p in coda.get("post", []) if p.get("tipo") == TIPO]
    print(f"voci threads in coda: {len(totali)} "
          f"(gia' pubblicate: {sum(1 for p in totali if p.get('pubblicato'))})")

    for pid, motivo in scarti:
        print(f"  [avviso] {pid}: {motivo}")

    if not voci:
        print("\nNiente da pubblicare adesso.")
        esiti = []
    else:
        print(f"\nDa pubblicare ({len(voci)}):")
        if vai:
            if not args.token:
                print("\n[ERRORE] manca il token: THREADS_TOKEN nell'ambiente oppure --token.")
                return 1
            print("    (il container non ha rete verso Meta: se sei li', questo fallira')")
        esiti = esegui(coda, args.coda, voci, args.token, args.user_id, vai)

    falliti = [e for e in esiti if e["esito"].startswith("errore")]
    print(f"\n=== fine · {sum(1 for e in esiti if e['esito'] == 'pubblicato')} pubblicati · "
          f"{len(falliti)} falliti · {len(scarti)} avvisi ===")
    if not vai and voci:
        print("Per pubblicare davvero: rilancia con --vai su una macchina con rete (Composio).")
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump({"quando": f"{adesso:%Y-%m-%d %H:%M} Roma", "vai": vai,
                       "esiti": esiti, "avvisi": [f"{a}: {b}" for a, b in scarti]},
                      f, ensure_ascii=False, indent=1)
    return 1 if falliti else 0


if __name__ == "__main__":
    sys.exit(main())

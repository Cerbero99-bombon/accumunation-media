# -*- coding: utf-8 -*-
"""Il pubblicatore. Gira su GitHub Actions, non dentro una sessione.

Perche' e' stato spostato qui (06/08/2026, dopo tre giorni di silenzio):
le sessioni schedulate di Cowork non riescono a usare il ponte verso Meta. Non
pubblicavano E non riuscivano nemmeno a dire di non aver pubblicato, perche' anche
il registro passava dallo stesso ponte. Un pubblicatore che dipende da una sessione
interattiva non e' un pubblicatore: e' un promemoria. Qui gira su una macchina di
GitHub, con Internet vero, i segreti del repo e un log che resta anche se crepa.

Regole (le stesse di prima, ora scritte in codice invece che in un prompt):
- esce solo cio' che ha pubblicato=false e la data gia' arrivata (ora di Roma);
- massimo 3 uscite per run;
- la coda si riscrive DOPO OGNI singola uscita: se crepa a meta', non esce due volte;
- prima di pubblicare si guarda cosa c'e' gia' online: se la didascalia combacia,
  la voce viene marcata e saltata;
- il permalink si scrive solo insieme a pubblicato=true, mai prima;
- un run che non pubblica niente lo dice lo stesso, con il motivo.

Segreti attesi: FB_PAGE_ID, FB_PAGE_TOKEN, IG_USER_ID, THREADS_USER_ID, THREADS_TOKEN
                IG_TOKEN (facoltativo: se c'e' si usa graph.instagram.com)
"""
import json, os, sys, time, datetime, urllib.parse, urllib.request, urllib.error, pathlib

ROMA = datetime.timezone(datetime.timedelta(hours=2))     # CEST
CODA = pathlib.Path("queue.json")
LOG = pathlib.Path("log-pubblicatore.md")
MAX = int(os.environ.get("MAX_USCITE", "3"))
PROVA = os.environ.get("PROVA", "") == "1"

FB_ID = os.environ.get("FB_PAGE_ID", "")
FB_TOK = os.environ.get("FB_PAGE_TOKEN", "")
IG_ID = os.environ.get("IG_USER_ID", "")
IG_TOK = os.environ.get("IG_TOKEN", "")
TH_ID = os.environ.get("THREADS_USER_ID", "")
TH_TOK = os.environ.get("THREADS_TOKEN", "")

GRAPH = "https://graph.facebook.com/v21.0"
IGAPI = "https://graph.instagram.com/v21.0"
THAPI = "https://graph.threads.net/v1.0"

righe = []


def nota(t):
    print(t, flush=True)
    righe.append(t)


def chiama(url, dati=None, metodo=None):
    corpo = urllib.parse.urlencode(dati).encode() if dati else None
    r = urllib.request.Request(url, data=corpo, method=metodo or ("POST" if dati else "GET"))
    try:
        with urllib.request.urlopen(r, timeout=90) as x:
            return json.loads(x.read().decode())
    except urllib.error.HTTPError as e:
        testo = e.read().decode()[:600]
        raise RuntimeError(f"HTTP {e.code} su {url.split('?')[0]} -> {testo}")


# ------------------------------------------------------------------ Instagram
def ig_base():
    """Dal 07/08 Instagram passa dal Graph con il token della Pagina: una chiave sola per
    IG e FB, che e' il motivo per cui il collegamento e' stato rifatto. IG_TOKEN resta
    come scavalco se un giorno servisse una chiave Instagram separata."""
    return (GRAPH, IG_TOK or FB_TOK)


def ig_contenitore(campi):
    b, t = ig_base()
    campi["access_token"] = t
    return chiama(f"{b}/{IG_ID}/media", campi)["id"]


def ig_pubblica(cid, attesa=180):
    b, t = ig_base()
    for _ in range(int(attesa / 5)):
        st = chiama(f"{b}/{cid}?fields=status_code&access_token={t}").get("status_code")
        if st == "FINISHED":
            break
        if st == "ERROR":
            raise RuntimeError(f"contenitore {cid} in ERROR")
        time.sleep(5)
    mid = chiama(f"{b}/{IG_ID}/media_publish", {"creation_id": cid, "access_token": t})["id"]
    try:
        link = chiama(f"{b}/{mid}?fields=permalink&access_token={t}").get("permalink", "")
    except Exception:
        link = ""
    return mid, link


def ig_recenti(n=12):
    b, t = ig_base()
    try:
        return chiama(f"{b}/{IG_ID}/media?fields=id,caption,timestamp,permalink&limit={n}&access_token={t}").get("data", [])
    except Exception as e:
        nota(f"  guardia IG non leggibile: {e}")
        return []


# ------------------------------------------------------------------ Facebook
def fb_foto(url, pubblicata=True, messaggio=None):
    d = {"url": url, "published": "true" if pubblicata else "false", "access_token": FB_TOK}
    if messaggio:
        d["message"] = messaggio
    return chiama(f"{GRAPH}/{FB_ID}/photos", d)["id"]


def fb_carosello(urls, messaggio):
    ids = [fb_foto(u, False) for u in urls]
    d = {"message": messaggio, "access_token": FB_TOK}
    for i, x in enumerate(ids):
        d[f"attached_media[{i}]"] = json.dumps({"media_fbid": x})
    return chiama(f"{GRAPH}/{FB_ID}/feed", d)["id"]


def fb_video(url, descrizione):
    return chiama(f"{GRAPH}/{FB_ID}/videos",
                  {"file_url": url, "description": descrizione, "access_token": FB_TOK})["id"]


def fb_storia(url):
    pid = fb_foto(url, False)
    r = chiama(f"{GRAPH}/{FB_ID}/photo_stories", {"photo_id": pid, "access_token": FB_TOK})
    return r.get("post_id") or r.get("id", "")


def fb_recenti(n=8):
    try:
        return chiama(f"{GRAPH}/{FB_ID}/feed?fields=id,message,created_time&limit={n}&access_token={FB_TOK}").get("data", [])
    except Exception as e:
        nota(f"  guardia FB non leggibile: {e}")
        return []


# ------------------------------------------------------------------ Threads
def th_pubblica(testo):
    c = chiama(f"{THAPI}/{TH_ID}/threads", {"media_type": "TEXT", "text": testo, "access_token": TH_TOK})["id"]
    time.sleep(3)
    mid = chiama(f"{THAPI}/{TH_ID}/threads_publish", {"creation_id": c, "access_token": TH_TOK})["id"]
    link = chiama(f"{THAPI}/{mid}?fields=permalink&access_token={TH_TOK}").get("permalink", "")
    return mid, link


# ------------------------------------------------------------------ coda
def quando(v):
    s = (v.get("quando") or "").replace(" Roma", "").strip()
    for f in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.datetime.strptime(s, f).replace(tzinfo=ROMA)
        except ValueError:
            pass
    return None


def testo_di(v):
    return v.get("caption") or v.get("testo") or v.get("titolo") or ""


def salva(q):
    CODA.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    adesso = datetime.datetime.now(ROMA)
    nota(f"## run {adesso:%Y-%m-%d %H:%M} Roma"
         + ("  ·  PROVA (non pubblica)" if PROVA else ""))
    q = json.loads(CODA.read_text(encoding="utf-8"))
    mature = [v for v in q["post"] if not v.get("pubblicato")
              and quando(v) and quando(v) <= adesso]
    mature.sort(key=quando)
    nota(f"- in coda mature: {len(mature)} · ne escono al massimo {MAX}")
    if not mature:
        futuri = [v for v in q["post"] if not v.get("pubblicato")]
        nota(f"- NIENTE DA PUBBLICARE: nessuna voce matura. Restano {len(futuri)} voci future.")
        return 0

    igr = ig_recenti() if IG_ID else []
    fbr = fb_recenti() if FB_ID else []
    fatti = saltati = 0

    for v in mature[:MAX]:
        vid, tipo = v["id"], v.get("tipo")
        testo = testo_di(v)
        primo = (testo.strip().split("\n")[0] or "")[:60]
        nota(f"### {vid} · {tipo} · previsto {v.get('quando')}")

        gia = [m for m in igr if primo and primo in (m.get("caption") or "")]
        if gia and tipo != "threads":
            v["pubblicato"] = True
            v["permalink"] = gia[0].get("permalink", "")
            v["nota"] = (v.get("nota") or "") + " | marcata dalla guardia: era gia' online."
            salva(q); saltati += 1
            nota(f"- GIA' ONLINE, marcata e saltata: {v['permalink']}")
            continue
        if PROVA:
            nota("- prova: mi fermo qui, non pubblico."); saltati += 1; continue

        try:
            if tipo == "threads":
                mid, link = th_pubblica(testo)
                v.update({"pubblicato": True, "threads_media_id": mid, "permalink": link})
                nota(f"- Threads: {link}")

            elif tipo == "reel":
                cid = ig_contenitore({"media_type": "REELS", "video_url": v["media"][0],
                                      "caption": testo, "share_to_feed": "false",
                                      **({"cover_url": v["cover"]} if v.get("cover") else {})})
                mid, link = ig_pubblica(cid)
                v.update({"pubblicato": True, "ig_media_id": mid, "permalink": link})
                nota(f"- Instagram: {link}")
                if not v.get("fb_pubblicato"):
                    v["fb_post_id"] = fb_video(v["media"][0], testo); v["fb_pubblicato"] = True
                    nota(f"- Facebook: {v['fb_post_id']}")

            elif tipo == "carosello":
                figli = [ig_contenitore({"image_url": u, "is_carousel_item": "true"}) for u in v["media"]]
                cid = ig_contenitore({"media_type": "CAROUSEL", "children": ",".join(figli), "caption": testo})
                mid, link = ig_pubblica(cid)
                v.update({"pubblicato": True, "ig_media_id": mid, "permalink": link})
                nota(f"- Instagram: {link}")
                if not v.get("fb_pubblicato"):
                    v["fb_post_id"] = fb_carosello(v["media"], testo); v["fb_pubblicato"] = True
                    nota(f"- Facebook: {v['fb_post_id']}")

            elif tipo in ("storia", "post"):
                if tipo == "storia":
                    cid = ig_contenitore({"media_type": "STORIES", "image_url": v["media"][0]})
                else:
                    cid = ig_contenitore({"image_url": v["media"][0], "caption": testo})
                mid, link = ig_pubblica(cid)
                v.update({"pubblicato": True, "ig_media_id": mid, "permalink": link})
                nota(f"- Instagram: {link or mid}")
                if not v.get("fb_pubblicato"):
                    v["fb_post_id"] = (fb_storia(v["media"][0]) if tipo == "storia"
                                       else fb_foto(v["media"][0], True, testo))
                    v["fb_pubblicato"] = True
                    nota(f"- Facebook: {v['fb_post_id']}")
            else:
                nota(f"- tipo sconosciuto '{tipo}': saltata."); saltati += 1; continue
            fatti += 1
        except Exception as e:
            nota(f"- ERRORE, voce NON marcata: {e}"); saltati += 1
        salva(q)

    restano = [v for v in q["post"] if not v.get("pubblicato")]
    nota(f"- chiuso: {fatti} pubblicati, {saltati} saltati, {len(restano)} restano in coda.")
    if len(restano) < 4:
        nota("- **LA CODA STA FINENDO**: meno di 4 voci non pubblicate.")
    return 0 if fatti or saltati == 0 else (0 if fatti else 1)


esito = 0
try:
    esito = main()
except Exception as e:
    nota(f"- CREPATO PRIMA DI PUBBLICARE: {e}")
    esito = 1
finally:
    vecchio = LOG.read_text(encoding="utf-8") if LOG.exists() else "# Registro del pubblicatore\n"
    LOG.write_text(vecchio.rstrip() + "\n\n" + "\n".join(righe) + "\n", encoding="utf-8")
sys.exit(esito)

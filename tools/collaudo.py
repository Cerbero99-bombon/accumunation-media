#!/usr/bin/env python3
"""Collaudo automatico dei reel. Il cancello PRIMA della consegna, non dopo.

Esiste perche' Enrico l'ha chiesto esplicitamente il 31/07/2026: il generatore deve essere
piu' pignolo di lui. La sua revisione e' un plus, non un passaggio del processo. Ogni reel
passa di qui e o esce PASS o non si consegna. Un difetto trovato da Enrico dopo un PASS
significa che manca un controllo: si aggiunge QUI, non ci si limita a correggere il video.

Uso:
    python3 tools/collaudo.py video.mp4 [words.json] [--cover cover.jpg]

Controlla:
  TECNICA    1080x1920, h264+aac, 30fps, durata sotto i 20s, audio presente
  LOUDNESS   -14 LUFS (+/-1), true peak <= -0.8 dBFS
  MOVIMENTO  nessuna finestra ferma oltre 1.5s (lo stile D e' movimento continuo)
  PARTENZA   il primo fotogramma non e' vuoto: il gancio sta nei primi 2 fotogrammi
  PALETTE    fondo caldo del brand, mai il navy freddo (errore gia' pagato due volte)
  ZONE UI    niente testo dove Instagram copre: ultimi 380px in basso, colonna destra
  SYNC       l'ultima parola finisce dentro il video, lo slogan ha il suo spazio
  BANDITE    OCR sui fotogrammi: italian|algoritm|made in (+ cover se passata)

Esce 0 con PASS (eventuali AVVISI stampati), 1 con FAIL.
Il collaudo NON sostituisce il guardare i fotogrammi: verifica cio' che si puo' misurare.
"""
import json, pathlib, re, subprocess, sys, tempfile

import numpy as np
from PIL import Image

FAIL, WARN, OK = "FAIL", "AVVISO", "ok"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(video):
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", video])
    return json.loads(r.stdout)


def estrai_frame(video, outdir, fps=4):
    run(["ffmpeg", "-y", "-v", "error", "-i", video,
         "-vf", f"fps={fps},scale=270:480", f"{outdir}/m%04d.png"])   # piccoli: per il movimento
    run(["ffmpeg", "-y", "-v", "error", "-i", video,
         "-vf", "fps=1", f"{outdir}/g%04d.png"])                      # grandi: per OCR e zone


def main():
    video = sys.argv[1]
    words = None
    cover = None
    args = sys.argv[2:]
    if args and not args[0].startswith("--"):
        words = args[0]
    if "--cover" in args:
        cover = args[args.index("--cover") + 1]

    esiti = []          # (livello, voce, dettaglio)
    def esito(liv, voce, det=""):
        esiti.append((liv, voce, det))

    # ---------- tecnica ----------
    p = probe(video)
    vs = next(s for s in p["streams"] if s["codec_type"] == "video")
    au = [s for s in p["streams"] if s["codec_type"] == "audio"]
    dur = float(p["format"]["duration"])
    if int(vs["width"]) == 1080 and int(vs["height"]) == 1920: esito(OK, "formato 1080x1920")
    else: esito(FAIL, "formato", f'{vs["width"]}x{vs["height"]}')
    if vs["codec_name"] == "h264": esito(OK, "h264")
    else: esito(FAIL, "codec video", vs["codec_name"])
    fr = vs.get("r_frame_rate", "0/1"); num, den = map(int, fr.split("/"))
    if den and round(num / den) == 30: esito(OK, "30 fps")
    else: esito(FAIL, "framerate", fr)
    if not au: esito(FAIL, "audio assente")
    elif au[0]["codec_name"] == "aac": esito(OK, "audio aac")
    else: esito(WARN, "audio non aac", au[0]["codec_name"])
    if dur <= 20.0: esito(OK, f"durata {dur:.1f}s")
    elif dur <= 20.6: esito(WARN, "durata al limite", f"{dur:.2f}s")
    else: esito(FAIL, "durata oltre i 20s", f"{dur:.2f}s — la regola e' sotto i 20")

    # ---------- loudness ----------
    if au:
        r = run(["ffmpeg", "-i", video, "-af",
                 "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"])
        m = re.search(r"\{[^{}]+\}", r.stderr[-2000:], re.S)
        if m:
            d = json.loads(m.group(0))
            I, TP = float(d["input_i"]), float(d["input_tp"])
            if -15.0 <= I <= -13.0: esito(OK, f"loudness {I:.1f} LUFS")
            else: esito(FAIL, "loudness fuori bersaglio", f"{I:.1f} LUFS (bersaglio -14)")
            if TP <= -0.8: esito(OK, f"true peak {TP:.1f}")
            else: esito(FAIL, "true peak alto", f"{TP:.1f} dBFS")

    # ---------- fotogrammi ----------
    with tempfile.TemporaryDirectory() as td:
        estrai_frame(video, td)
        piccoli = sorted(pathlib.Path(td).glob("m*.png"))
        grandi = sorted(pathlib.Path(td).glob("g*.png"))
        M = [np.asarray(Image.open(f).convert("L"), dtype=np.int16) for f in piccoli]

        # partenza: il gancio nei primi 2 fotogrammi
        primo = M[0]
        if (primo > 60).mean() > 0.004: esito(OK, "primo fotogramma pieno")
        else: esito(FAIL, "primo fotogramma vuoto", "il gancio deve esserci dal fotogramma 1")

        # movimento: differenza media fra fotogrammi consecutivi (4 al secondo)
        fermi = 0; buco = 0
        for a, b in zip(M, M[1:]):
            diff = np.abs(a - b).mean()
            if diff < 0.22: fermi += 1; buco = max(buco, fermi)
            else: fermi = 0
        finestra_ferma = buco * 0.25
        if finestra_ferma <= 1.5: esito(OK, f"movimento continuo (max fermo {finestra_ferma:.2f}s)")
        else: esito(FAIL, "video fermo", f"{finestra_ferma:.2f}s senza movimento percettibile")

        # palette: il fondo deve essere caldo. Si giudicano SOLO i pixel scuri (il fondo),
        # e freddo vuol dire blu sopra il rosso E sopra il verde: cosi' il verde del brand
        # e il blu degli accenti non fanno scattare falsi allarmi.
        freddi, scuri = 0, 0
        for f in piccoli[:: max(1, len(piccoli) // 8)]:
            rgb = np.asarray(Image.open(f).convert("RGB"), dtype=np.int16)
            luma = 0.3 * rgb[:, :, 0] + 0.59 * rgb[:, :, 1] + 0.11 * rgb[:, :, 2]
            scuro = luma < 90
            freddo = scuro & (rgb[:, :, 2] > rgb[:, :, 0] + 6) & (rgb[:, :, 2] >= rgb[:, :, 1])
            scuri += int(scuro.sum()); freddi += int(freddo.sum())
        quota = freddi / max(1, scuri)
        if quota < 0.20: esito(OK, "fondo caldo")
        else: esito(FAIL, "fondo freddo/navy", f"{quota * 100:.0f}% del fondo e' blu-freddo")

        # zone coperte dalla UI di Instagram: testo negli ultimi 380px o nella colonna destra
        # (controllo sui frame grandi, luminanza alta = testo)
        basso_sporchi = 0; destra_sporchi = 0
        for f in grandi:
            g = np.asarray(Image.open(f).convert("L"), dtype=np.uint8)
            if (g[1560:1880, 60:1020] > 190).mean() > 0.004: basso_sporchi += 1
            if (g[980:1680, 966:1080] > 190).mean() > 0.004: destra_sporchi += 1
        if basso_sporchi / len(grandi) <= 0.15: esito(OK, "fascia bassa libera (UI Instagram)")
        else: esito(FAIL, "testo nella fascia bassa", f"{basso_sporchi}/{len(grandi)} fotogrammi: li' Instagram copre con caption e icone")
        if destra_sporchi / len(grandi) <= 0.25: esito(OK, "colonna destra libera")
        else: esito(WARN, "testo sotto le icone di destra", f"{destra_sporchi}/{len(grandi)} fotogrammi")

        # bandite: OCR su tutti i frame grandi + cover
        testo_ocr = []
        da_leggere = list(grandi) + ([pathlib.Path(cover)] if cover else [])
        for f in da_leggere:
            r = run(["tesseract", str(f), "-", "--psm", "11"])
            testo_ocr.append(r.stdout.lower())
        tutto = "\n".join(testo_ocr)
        m = re.search(r"italian|algoritm|made in", tutto)
        if not m: esito(OK, "nessuna affermazione bandita (OCR)")
        else: esito(FAIL, "affermazione bandita a schermo", m.group(0))

    # ---------- sincronia ----------
    if words:
        w = json.load(open(words))
        fine = max(x[1] for x in w)
        if fine <= dur - 0.15: esito(OK, f"voce dentro il video ({fine:.1f}s su {dur:.1f})")
        else: esito(FAIL, "voce tagliata", f"ultima parola a {fine:.2f}s, video {dur:.2f}s")

    # ---------- verdetto ----------
    fail = [e for e in esiti if e[0] == FAIL]
    avvisi = [e for e in esiti if e[0] == WARN]
    for liv, voce, det in esiti:
        print(f"[{liv:6}] {voce}" + (f" — {det}" if det else ""))
    print()
    if fail:
        print(f"COLLAUDO: BOCCIATO ({len(fail)} difetti). Non si consegna.")
        sys.exit(1)
    print(f"COLLAUDO: PASS" + (f" con {len(avvisi)} avvisi" if avvisi else "") +
          ". Resta obbligatorio guardare il provino dei fotogrammi.")


if __name__ == "__main__":
    main()

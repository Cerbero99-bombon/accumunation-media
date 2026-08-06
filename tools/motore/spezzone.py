# -*- coding: utf-8 -*-
"""Aggancia lo spezzone al reel con una transizione DISEGNATA su quel reel.

Perche' non una transizione sola per tutti: una dissolvenza uguale ogni volta e' un
taglio, non un'idea. Qui ogni reel ha la sua, scelta sul contenuto: il vetro che si
rompe entra a schegge, il peso che cade entra dall'alto, il prezzo che non e' mai
esistito si sgretola. Chi guarda non la sa nominare ma la sente coerente.

Come regge la memoria (la sandbox ha 985 MB e ricodificare un reel intero la satura):
si ricodificano SOLO lo spezzone e il primo secondo e mezzo del reel. Il resto del
video passa in copia dentro un contenitore mpegts. L'audio invece si rifa' tutto in
una passata: e' leggero e cosi' il sincrono resta esatto al campione.

  python3 spezzone.py <hook.mp4> <reel.mp4> <out.mp4> <nome-transizione> [inizio_hook]
"""
import json, subprocess, sys

W, H, FPS = 1080, 1920, 30
TAGLIO = 1.5          # dove si stacca il reel: con -g 15 e' un fotogramma chiave esatto
DUR_HOOK = 2.4

# nome -> (transizione xfade, durata, effetto sulla coda dello spezzone, perche')
TRANSIZIONI = {
 "schegge":  ("hlslice",    0.35, "flash",  "il vetro si spacca: il fotogramma va in schegge"),
 "impatto":  ("coverdown",  0.30, None,     "il peso cade dall'alto e copre"),
 "sterzata": ("smoothleft", 0.30, "mosso",  "la domanda si gira dall'altra parte"),
 "sgretola": ("pixelize",   0.45, None,     "cio' che non e' mai esistito si sgretola"),
 "riempi":   ("revealup",   0.40, None,     "il conto si riempie dal basso"),
 "spinta":   ("zoomin",     0.30, "fermo",  "la spinta: un colpo in avanti"),
 "giro":     ("squeezev",   0.35, None,     "il giro completo"),
 "capriola": ("squeezeh",   0.35, None,     "il capitombolo"),
 "scatto":   ("fadewhite",  0.12, "nero",   "salta la corrente e riparte da capo"),
 "addosso":  ("circleclose",0.30, None,     "la pressione che si chiude addosso"),
 "stacco":   ("fadeblack",  0.16, None,     "cambio di scena netto"),
 "caduta":   ("slideup",    0.32, None,     "arrivare giu' per primi"),
 "cerchio":  ("circleopen", 0.40, None,     "il cerchio gia' in scena diventa la porta"),
 "frana":    ("hrwind",     0.40, None,     "la frana che passa"),
}


def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-1500:]); raise SystemExit(1)
    return r.stdout.strip()


def dur(f):
    return float(sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{f}"'))


def main(hook, reel, out, nome, inizio=None, lungh=None):
    tr, xd, extra, perche = TRANSIZIONI[nome]
    dh = dur(hook); dr = dur(reel)
    ini = float(inizio) if inizio is not None else max(0.0, dh - DUR_HOOK)
    lh = min(float(lungh) if lungh else DUR_HOOK, dh - ini)

    # 1. spezzone normalizzato: riempie il 9:16, 30 fps, senza audio (l'audio si fa dopo)
    base = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    coda = ""
    if extra == "flash":
        coda = f",eq=brightness='0.42*max(0\\,(t-{lh-xd-0.10:.2f})/0.28)'"
    elif extra == "mosso":
        # la panoramica vera: si allarga il fotogramma e lo si fa scorrere sull'ultimo mezzo secondo
        base = (f"scale={int(W*1.18)}:{int(H*1.18)}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H}:x='(iw-{W})/2+(iw-{W})/2*min(1\\,max(0\\,(t-{lh-xd-0.18:.2f})/{xd+0.18:.2f}))':y=(ih-{H})/2")
    elif extra == "nero":
        coda = f",eq=brightness='if(gt(t,{lh-0.07:.2f}),-1,0)'"
    sh(f'ffmpeg -y -loglevel error -ss {ini} -t {lh} -i "{hook}" -an '
       f'-vf "{base},fps={FPS},setsar=1{coda}" '
       f'-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -g 15 -keyint_min 15 -sc_threshold 0 _sp.mp4')
    if extra == "fermo":   # un fermo immagine breve prima dello scatto in avanti
        sh(f'ffmpeg -y -loglevel error -i _sp.mp4 -vf "tpad=stop_mode=clone:stop_duration=0.15" '
           f'-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -g 15 -keyint_min 15 -sc_threshold 0 _sp2.mp4 && mv _sp2.mp4 _sp.mp4')
        lh += 0.15

    # 2. testa del reel (1.5 s) e transizione: si ricodifica solo questo
    sh(f'ffmpeg -y -loglevel error -t {TAGLIO} -i "{reel}" -an -c:v libx264 -preset veryfast -crf 18 '
       f'-pix_fmt yuv420p -g 15 -keyint_min 15 -sc_threshold 0 _testa.mp4')
    off = round(lh - xd, 3)
    sh(f'ffmpeg -y -loglevel error -i _sp.mp4 -i _testa.mp4 -filter_complex '
       f'"[0:v][1:v]xfade=transition={tr}:duration={xd}:offset={off},fps={FPS},setsar=1[v]" -map "[v]" '
       f'-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -g 15 -keyint_min 15 -sc_threshold 0 _giunta.mp4')

    # 3. video: giunta + resto del reel, in COPIA (niente ricodifica del corpo)
    sh(f'ffmpeg -y -loglevel error -ss {TAGLIO} -i "{reel}" -an -c:v copy -bsf:v h264_mp4toannexb -f mpegts _b.ts')
    sh(f'ffmpeg -y -loglevel error -i _giunta.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts _a.ts')
    sh('ffmpeg -y -loglevel error -i "concat:_a.ts|_b.ts" -c copy -bsf:v h264_mp4toannexb _video.mp4')

    # 4. audio in una passata sola: spezzone (sotto) che sfuma nella traccia del reel
    sh(f'ffmpeg -y -loglevel error -ss {ini} -t {lh} -i "{hook}" -i "{reel}" -filter_complex '
       f'"[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.72,'
       f'afade=t=in:st=0:d=0.15[a0];'
       f'[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a1];'
       f'[a0][a1]acrossfade=d={xd}:c1=tri:c2=tri[a]" -map "[a]" -c:a aac -b:a 160k _audio.m4a')

    sh(f'ffmpeg -y -loglevel error -i _video.mp4 -i _audio.m4a -c:v copy -c:a copy -movflags +faststart "{out}"')
    print(json.dumps({"out": out, "transizione": nome, "xfade": tr, "durata_x": xd,
                      "perche": perche, "spezzone": round(lh, 2),
                      "durata": round(dur(out), 2)}, ensure_ascii=False))


main(*sys.argv[1:])

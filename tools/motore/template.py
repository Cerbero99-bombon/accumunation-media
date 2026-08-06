# -*- coding: utf-8 -*-
"""Spezzoni-modello: i riquadri grigi NON sono uno scarto, sono il posto nostro.

Alcuni clip di viralhooks alternano la reazione di una persona a riquadri grigi con
scritto YOUR PRODUCT SHOT. Il 07/08 li avevo evitati come se fossero un difetto: e'
il contrario, sono il formato. Chi guarda vede uno che si stupisce, e si stupisce di
CIO' CHE METTIAMO NOI. Buttare quei clip vuol dire buttare il gancio migliore.

Qui il video dei riquadri viene sostituito e l'audio originale resta continuo: la
reazione non si spezza. Gli slot si trovano da soli (fotogrammi piatti), non a occhio.

  python3 template.py <clip.mp4> <out.mp4> <inserto1.mp4[,da]> [inserto2.mp4[,da]] ...
"""
import json, subprocess, statistics, sys

W, H, FPS = 1080, 1920, 30


def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-1500:]); raise SystemExit(1)
    return r.stdout.strip()


def slot(f, soglia=14.0, minimo=0.4):
    """I tratti in cui il fotogramma e' piatto: sono i riquadri da riempire."""
    w, h, fps = 64, 114, 10
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf',
                          f'fps={fps},scale={w}:{h},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True).stdout
    n = len(raw) // (w * h); out = []; cur = None
    for i in range(n):
        piatto = statistics.pstdev(raw[i * w * h:(i + 1) * w * h]) < soglia
        t = i / fps
        if piatto and cur is None: cur = t
        if not piatto and cur is not None:
            if t - cur >= minimo: out.append((round(cur, 2), round(t - 1 / fps, 2)))
            cur = None
    if cur is not None and n / fps - cur >= minimo: out.append((round(cur, 2), round(n / fps, 2)))
    return out, n / fps


def main(clip, out, *inserti):
    slots, dur = slot(clip)
    if not slots:
        print("nessun riquadro da riempire: usa spezzone.py"); raise SystemExit(1)
    print("riquadri trovati:", slots)
    usa = list(zip(slots, inserti))

    V = ("-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -g 15 -keyint_min 15 -sc_threshold 0")
    SC = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1"
    # a pezzi e in fila: tre stream insieme a 1080x1920 non ci stanno in memoria (provato, ucciso)
    pezzi, t = [], 0.0
    for k, ((a, b), spec) in enumerate(usa, start=1):
        if a - t > 0.05:
            sh(f'ffmpeg -y -loglevel error -ss {t} -t {a-t:.2f} -i "{clip}" -an -vf "{SC}" {V} _p{k}a.mp4')
            pezzi.append(f'_p{k}a.mp4')
        c = spec.split(','); src = c[0]; da = float(c[1]) if len(c) > 1 else 0.0
        L = round(b - a, 2)
        # spinta lenta in avanti: il riquadro non deve sembrare una fotografia incollata
        sh(f'ffmpeg -y -loglevel error -ss {da} -t {L} -i "{src}" -an -vf '
           f'"scale={int(W*1.10)}:{int(H*1.10)}:force_original_aspect_ratio=increase,'
           f'crop={W}:{H}:(iw-{W})/2:(ih-{H})/2,fps={FPS},setsar=1,'
           f'fade=t=in:st=0:d=0.10,fade=t=out:st={L-0.10:.2f}:d=0.10" {V} _p{k}b.mp4')
        pezzi.append(f'_p{k}b.mp4')
        t = b
    if dur - t > 0.05:
        sh(f'ffmpeg -y -loglevel error -ss {t} -i "{clip}" -an -vf "{SC}" {V} _pz.mp4')
        pezzi.append('_pz.mp4')

    for i, p in enumerate(pezzi):
        sh(f'ffmpeg -y -loglevel error -i {p} -c copy -bsf:v h264_mp4toannexb -f mpegts _t{i}.ts')
    cat = "|".join(f"_t{i}.ts" for i in range(len(pezzi)))
    sh(f'ffmpeg -y -loglevel error -i "concat:{cat}" -c copy -bsf:v h264_mp4toannexb _muto.mp4')
    sh(f'ffmpeg -y -loglevel error -i "{clip}" -vn -c:a aac -b:a 160k _voce.m4a')
    sh(f'ffmpeg -y -loglevel error -i _muto.mp4 -i _voce.m4a -c:v copy -c:a copy -shortest "{out}"')
    print(json.dumps({"out": out, "riquadri": slots, "pezzi": len(pezzi),
                      "durata": float(sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{out}"'))},
                     ensure_ascii=False))


main(*sys.argv[1:])

# -*- coding: utf-8 -*-
"""Voce del brand, registro per registro. Scelta di Enrico il 06/08/2026: la "I".

Perche' cosi' e non con SSML: l'endpoint Read Aloud accetta SOLO
<speak><voice><prosody pitch rate volume>. <break>, <mstts:express-as>, contour,
<emphasis> e <mstts:silence> non tornano audio. L'espressivita' quindi non si
chiede al motore: si costruisce fuori, una frase alla volta, con il suo ritmo,
la sua pausa e il suo corpo (EQ). Misurato, non stimato.

"Stoico" per Enrico NON vuol dire lento: vuol dire uniforme. Abbassare il pitch
assottiglia questa voce e la fa sembrare vecchia (bocciato il 06/08). Il corpo
arriva dall'equalizzatore, non dal tono.

  python3 voce.py copione.json voce.wav words.json
  copione.json = [{"t": "frase", "reg": "apertura|corpo|perno|chiusura"}, ...]
"""
import asyncio, json, subprocess, sys, edge_tts

VOCE = "de-DE-SeraphinaMultilingualNeural"

# registro: (rate, pitch, pausa PRIMA, pausa DOPO)
REG = {
    "apertura": ("+7%", "+0Hz", 0.00, 0.20),
    "corpo":    ("+9%", "+0Hz", 0.04, 0.17),
    "perno":    ("+1%", "+0Hz", 0.30, 0.26),
    "chiusura": ("+3%", "+0Hz", 0.28, 0.40),
}

# il corpo: 190Hz su, 520Hz giu' (la nasalita'), presenza a 2.8k, sibilanti a 7k giu'
PETTO = ("highpass=f=90,equalizer=f=190:t=q:w=1.0:g=4,equalizer=f=520:t=q:w=1.2:g=-2.5,"
         "equalizer=f=2800:t=q:w=1.4:g=2,equalizer=f=7000:t=q:w=2.0:g=-2.5,"
         "acompressor=threshold=0.15:ratio=4:attack=6:release=140,"
         "loudnorm=I=-16:TP=-1.5:LRA=6")


def sh(c):
    subprocess.run(c, shell=True, check=True)


def dur(f):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
        capture_output=True, text=True).stdout.strip())


async def frase(testo, rate, pitch, out):
    c = edge_tts.Communicate(testo, VOCE, rate=rate, pitch=pitch, boundary="WordBoundary")
    w = []
    with open(out, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                w.append([ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]])
    return w


async def main(copione, wav_out, words_out):
    righe = json.load(open(copione, encoding="utf-8"))
    parole, t0, pezzi = [], 0.0, []
    for i, r in enumerate(righe):
        rate, pitch, prima, dopo = REG[r.get("reg", "corpo")]
        if prima > 0:
            s = f"p{i:02d}.wav"
            sh(f'ffmpeg -y -loglevel error -f lavfi -i anullsrc=r=48000:cl=mono -t {prima} {s}')
            pezzi.append(s); t0 += prima
        mp3, wav = f"b{i:02d}.mp3", f"b{i:02d}.wav"
        w = await frase(r["t"], rate, pitch, mp3)
        sh(f'ffmpeg -y -loglevel error -i {mp3} -ar 48000 -ac 1 {wav}')
        for a, b, tx in w:
            parole.append([round(t0 + a, 3), round(t0 + b, 3), tx, i])
        pezzi.append(wav); t0 += dur(wav)
        if dopo > 0:
            s = f"d{i:02d}.wav"
            sh(f'ffmpeg -y -loglevel error -f lavfi -i anullsrc=r=48000:cl=mono -t {dopo} {s}')
            pezzi.append(s); t0 += dopo
    with open("lista.txt", "w") as f:
        for p in pezzi:
            f.write(f"file '{p}'\n")
    sh('ffmpeg -y -loglevel error -f concat -safe 0 -i lista.txt -c copy _grezza.wav')
    sh(f'ffmpeg -y -loglevel error -i _grezza.wav -af "{PETTO}" -ar 48000 -ac 1 {wav_out}')
    json.dump(parole, open(words_out, "w"), ensure_ascii=False)
    print(f"{wav_out} · {len(parole)} parole · {len(righe)} frasi · {round(t0,2)}s")


asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))

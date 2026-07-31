"""Voce del brand a blocchi: ogni frase ha il suo ritmo, il suo tono e la sua pausa dopo.
E' cosi' che si ottiene l'espressivita': non da una voce piu' brava, ma da una lettura diretta.
Restituisce voce.wav + words.json coi tempi assoluti gia' corretti per le pause."""
import asyncio, json, subprocess, sys, edge_tts, os

VOCE = "fr-FR-RemyMultilingualNeural"

async def blocco(testo, rate, pitch, out):
    c = edge_tts.Communicate(testo, VOCE, rate=rate, pitch=pitch, boundary="WordBoundary")
    w = []
    with open(out, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                w.append([ch["offset"]/1e7, (ch["offset"]+ch["duration"])/1e7, ch["text"]])
    return w

async def main(spec_path, wav_out, words_out):
    spec = json.load(open(spec_path, encoding="utf-8"))
    parole, t0, pezzi = [], 0.0, []
    for i, b in enumerate(spec):
        mp3 = f"b{i:02d}.mp3"; wav = f"b{i:02d}.wav"
        w = await blocco(b["t"], b.get("rate","+0%"), b.get("pitch","+0Hz"), mp3)
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",mp3,"-ar","48000","-ac","1",wav], check=True)
        d = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                  "-of","csv=p=0",wav], capture_output=True, text=True).stdout.strip())
        for a, bb, tx in w:
            parole.append([round(t0+a,3), round(t0+bb,3), tx, i])
        pezzi.append(wav)
        pausa = b.get("pausa", 0.0)
        t0 += d + pausa
        if pausa > 0:
            sil = f"s{i:02d}.wav"
            subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",
                            f"anullsrc=r=48000:cl=mono","-t",str(pausa),sil], check=True)
            pezzi.append(sil)
    with open("lista.txt","w") as f:
        for p in pezzi: f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","lista.txt",
                    "-c","copy",wav_out], check=True)
    json.dump(parole, open(words_out,"w"), ensure_ascii=False)
    print(f"{wav_out} · {len(parole)} parole · {round(t0,2)}s")

asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))

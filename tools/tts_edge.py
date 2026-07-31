#!/usr/bin/env python3
"""Genera la voce del brand e i tempi parola-per-parola.

GIRA SOLO SU UNA MACCHINA CON RETE (COMPOSIO_REMOTE_BASH_TOOL), non nel container:
l'endpoint Microsoft non e' raggiungibile da dentro.

  pip install edge-tts
  python3 tts_edge.py "il testo del reel" voce.mp3 words.json

Poi si converte e si committa nel repo, e il montaggio prosegue nel container:
  ffmpeg -y -i voce.mp3 -ar 48000 -ac 1 voce.wav
"""
import asyncio, sys, json, edge_tts

VOCE = "it-IT-DiegoNeural"   # alternative: ElsaNeural (F), IsabellaNeural (F), GiuseppeMultilingualNeural (M)
RITMO = "+8%"


async def main(testo, out_audio, out_words):
    c = edge_tts.Communicate(testo, VOCE, rate=RITMO, boundary="WordBoundary")
    parole = []
    with open(out_audio, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                parole.append([ch["offset"] / 1e7,
                               (ch["offset"] + ch["duration"]) / 1e7,
                               ch["text"]])
    json.dump(parole, open(out_words, "w"), ensure_ascii=False)
    print(f"{out_audio} · {len(parole)} parole · {parole[-1][1]:.2f}s")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))

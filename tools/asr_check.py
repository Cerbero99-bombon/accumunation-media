#!/usr/bin/env python3
"""Cancello ASR: riascolta OGNI blocco di voce e lo confronta col copione.

Nato il 01/08/2026, dopo che Remy (voce multilingue francese) ha letto "Buttati" come
"potati" e "Mai indossata" storpiato, e nessun controllo l'ha sentito: i cancelli
verificavano i pixel, non il suono. Gira sulla macchina con rete (faster-whisper).

Uso: python3 asr_check.py s.json cartella_blocchi/
Esce 1 se anche un solo blocco ha parole storpiate. In quel caso NON si monta:
si riscrive il blocco (piu' contesto, grafia fonetica) e si rigenera.
"""
import sys, json, re, unicodedata
from faster_whisper import WhisperModel

NUM = {"ottantacinque":"85","trentasette":"37","trecentomila":"300000","venti":"20",
       "duemiladiciannove":"2019","duemilaventitre":"2023","centotrenta":"130",
       "cinquanta":"50","diciannove":"19","cinquecento":"500","trecentonovantatre":"393",
       "novanta":"90","sette":"7","dieci":"10","cento":"100"}

def deacc(s): return ''.join(c for c in unicodedata.normalize('NFD',s)
                             if unicodedata.category(c)!='Mn')
def norm(s):
    s = deacc(s.lower())
    return re.sub(r"[^a-z0-9 ]"," ",s).split()

def lev(a,b):
    if abs(len(a)-len(b))>2: return 99
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]+[0]*len(b)
        for j,cb in enumerate(b,1):
            cur[j]=min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb))
        prev=cur
    return prev[-1]

spec = json.load(open(sys.argv[1], encoding="utf-8")); bdir = sys.argv[2]
model = WhisperModel("base", device="cpu", compute_type="int8")
falliti = 0
for i,b in enumerate(spec):
    segs,_ = model.transcribe(f"{bdir}/b{i:02d}.wav", language="it")
    tr = " ".join(s.text for s in segs).strip()
    tw = norm(tr); joined = "".join(tw)
    manca = []
    for w in norm(b["t"]):
        if len(w)<4: continue
        if any(lev(w,x)<=1 for x in tw): continue
        if w in joined: continue
        if w in NUM and NUM[w] in joined: continue
        manca.append(w)
    if manca: falliti += 1
    print(f"[{'FAIL' if manca else 'ok  '}] b{i:02d} atteso: {b['t']}")
    print(f"        sentito: {tr}")
    if manca: print(f"        storpiate: {manca}")
print("ASR:", "PASS" if falliti==0 else f"BOCCIATO ({falliti} blocchi storpiati)")
sys.exit(1 if falliti else 0)

#!/usr/bin/env python3
"""Cancello ASR: riascolta OGNI blocco di voce e lo confronta col copione.

Nato il 01/08/2026, dopo che Remy (voce multilingue francese) ha letto "Buttati" come
"potati" e "Mai indossata" storpiato, e nessun controllo l'ha sentito: i cancelli
verificavano i pixel, non il suono. Gira sulla macchina con rete (faster-whisper).

Uso:
  python3 asr_check.py s.json cartella_blocchi/           # blocchi b*.wav gia' separati
  python3 asr_check.py s.json voce.wav words.json         # taglia i blocchi dal wav intero
Esce 1 se anche un solo blocco ha parole storpiate. In quel caso NON si monta:
si riscrive il blocco (piu' contesto, grafia fonetica) e si rigenera.

Il modello: di serie usa la copia LOCALE nel container (/tmp/asrm), montata dal ramo
`asr-model` del repo (cat parte_a* > model.bin). Le macchine remote da 1GB uccidono
il modello base per RAM e il tiny da' falsi positivi perfino sullo slogan: il riascolto
si fa qui. Override con ASR_MODEL (nome o percorso).
"""
import sys, json, re, unicodedata, os, subprocess, tempfile
from faster_whisper import WhisperModel

NUM = {"ottantacinque":["85"],"trentasette":["37"],"trecentomila":["300000","300mila"],
       "venti":["20"],"duemiladiciannove":["2019"],"duemilaventitre":["2023"],
       "centotrenta":["130"],"cinquanta":["50"],"diciannove":["19"],"cinquecento":["500"],
       "trecentonovantatre":["393"],"novanta":["90"],"dieci":["10"],"cento":["100"],
       "duemilioni":["2milioni"],"ventimila":["20mila","20000"],
       "cinquemila":["5000","5mila"],"ottocentonovanta":["890"],"cinquecento":["500"],
       "cinque":["5"],"chili":["kg"],"sette":["7"],"otto":["8"],"nove":["9"],"quattro":["4"],
       "trenta":["30"],"quaranta":["40"],"sessanta":["60"],"settanta":["70"],
       "ottanta":["80"],"mille":["1000"],"ventotto":["28"],"quindicimila":["15000","15mila"],
       "duemilaventidue":["2022"],"quattrocento":["400"],"centoquarantotto":["148"],
       "tremila":["3000","3mila"],"quattro":["4"],"duemiladiciotto":["2018"]}

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

spec = json.load(open(sys.argv[1], encoding="utf-8"))
model = WhisperModel(os.environ.get("ASR_MODEL","/tmp/asrm"), device="cpu", compute_type="int8")

def blocchi():
    if len(sys.argv) == 3:                        # cartella con b*.wav
        for i,b in enumerate(spec):
            f = f"{sys.argv[2]}/b{i:02d}.wav"
            g = tempfile.mktemp(suffix=".wav")    # sempre a 16k mono: a 48k il modello sragiona
            subprocess.run(["ffmpeg","-y","-v","error","-i",f,"-ar","16000","-ac","1",g],check=True)
            yield i,b,g
    else:                                          # wav intero + words.json coi tempi
        words = json.load(open(sys.argv[3], encoding="utf-8"))
        for i,b in enumerate(spec):
            g = [w for w in words if w[3]==i]
            a = max(0, g[0][0]-0.15)
            fine = words[[w[3] for w in words].index(i+1)][0]-0.05 if any(w[3]==i+1 for w in words) else 1e6
            f = tempfile.mktemp(suffix=".wav")
            subprocess.run(["ffmpeg","-y","-v","error","-ss",str(a),"-to",str(min(fine,g[-1][1]+b.get("pausa",0.3)+0.15)),
                            "-i",sys.argv[2],"-ar","16000","-ac","1",f],check=True)
            yield i,b,f

def prova(wav, testo):
    """Il decoder int8 non e' deterministico: su audio identico ogni tanto collassa su
    output vuoto o troncato. Tre tentativi, si tiene il migliore: un blocco e' buono se
    ALMENO un tentativo lo sente pulito (il difetto vero e' stabile, il collasso no)."""
    meglio=None
    for _ in range(3):
        segs,_ = model.transcribe(wav, language="it", beam_size=5,
                                  temperature=0.0, condition_on_previous_text=False)
        tr = " ".join(s.text for s in segs).strip()
        tw = norm(tr); joined = "".join(tw)
        manca = []
        for w in norm(testo):
            if len(w)<4: continue
            if any(lev(w,x)<=1 for x in tw): continue
            if w in joined: continue
            if w in NUM and any(v in joined for v in NUM[w]): continue
            manca.append(w)
        if meglio is None or len(manca)<len(meglio[0]): meglio=(manca,tr)
        if not manca: break
    return meglio

falliti = 0
for i,b,wav in blocchi():
    manca, tr = prova(wav, b["t"])
    if manca: falliti += 1
    print(f"[{'FAIL' if manca else 'ok  '}] b{i:02d} atteso: {b['t']}")
    print(f"        sentito: {tr}")
    if manca: print(f"        storpiate: {manca}")
print("ASR:", "PASS" if falliti==0 else f"BOCCIATO ({falliti} blocchi storpiati)")
sys.exit(1 if falliti else 0)

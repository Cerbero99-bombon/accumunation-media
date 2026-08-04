#!/usr/bin/env python3
"""Controllo di salute della coda: passato coerente, futuro pubblicabile.
Uso: python3 tools/controllo_coda.py [--rete]  (--rete verifica anche gli URL con curl)"""
import json, sys, subprocess, datetime
q=json.load(open('queue.json')); oggi=datetime.date(2026,8,4)
oggi=datetime.date.today()
err=[]; warn=[]
visti=set()
rete='--rete' in sys.argv
def urlok(u):
    r=subprocess.run(['curl','-sI','-o','/dev/null','-w','%{http_code}',u],capture_output=True,text=True)
    return r.stdout.strip()=='200'
giorni_storia=set()
for p in q['post']:
    pid=p.get('id',p['titolo'])
    if pid in visti: err.append(f"id duplicato: {pid}")
    visti.add(pid)
    d=datetime.date.fromisoformat(p['quando'][:10])
    if p['pubblicato']:
        if p['tipo']!='storia' and not p.get('permalink'): err.append(f"{pid}: pubblicato senza permalink")
        if d>oggi: err.append(f"{pid}: pubblicato ma data futura {d}")
    else:
        if d<oggi: err.append(f"{pid}: NON pubblicato con data passata {d} — buco o task fermo")
        if p['tipo'] in ('reel','carosello') and not p.get('caption'): err.append(f"{pid}: senza caption")
        if p['tipo']=='reel' and not p.get('cover'): warn.append(f"{pid}: reel senza cover")
        if p.get('permalink'): err.append(f"{pid}: non pubblicato ma con permalink")
        if rete:
            # le voci threads sono di solo testo: nessun media da verificare
            for u in p.get('media',[])+([p['cover']] if p.get('cover') else []):
                if not urlok(u): err.append(f"{pid}: URL non raggiungibile {u[-60:]}")
        if p['tipo']=='storia': giorni_storia.add(d)
# una storia al giorno, da domani all'ultima programmata
fut=[datetime.date.fromisoformat(p['quando'][:10]) for p in q['post'] if not p['pubblicato']]
if fut:
    ultima=max(giorni_storia) if giorni_storia else oggi
    g=oggi+datetime.timedelta(days=1)
    while g<=ultima:
        if g not in giorni_storia: err.append(f"manca la storia del {g}")
        g+=datetime.timedelta(days=1)
    fine=max(fut)
    if ultima<fine: warn.append(f"storie coperte solo fino al {ultima}, la coda arriva al {fine}: produrre il lotto prima del {ultima}")
# due uscite stesso tipo stesso giorno
from collections import Counter
c=Counter((p['quando'][:10],p['tipo']) for p in q['post'] if not p['pubblicato'])
for k,v in c.items():
    if v>1: err.append(f"{v} {k[1]} lo stesso giorno {k[0]}")
for e in err: print("[ERRORE]",e)
for w in warn: print("[avviso]",w)
print("CODA:","GUASTA" if err else "SANA",f"· {len([p for p in q['post'] if not p['pubblicato']])} futuri · avvisi: {len(warn)}")
sys.exit(1 if err else 0)

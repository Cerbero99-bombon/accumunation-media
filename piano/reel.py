#!/usr/bin/env python3
"""Griglia dei reel: moltiplicazione a 4 fattori con filtro.

problema x rubrica x angolo x destinatario. Il valore non e' la moltiplicazione,
e' il filtro: la matrice di compatibilita' qui sotto scarta le combinazioni deboli
prima che qualcuno ci perda tempo.

USO
  python3 piano/reel.py init        # costruisce reel.json
  python3 piano/reel.py liberi      # combinazioni ancora disponibili
  python3 piano/reel.py usa <id> <post> <data>
  python3 piano/reel.py dashboard   # rigenera piano/griglia-reel.html
"""
import json, io, os, sys, html

QUI = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(QUI, 'reel.json')
DASH = os.path.join(QUI, 'griglia-reel.html')

COMPRA, PRODUCE = 'chi compra', 'chi produce'

PROBLEMI = [
    ('P01', COMPRA,  "Ho pagato troppo e l'ho scoperto dopo"),
    ('P02', COMPRA,  "Pagare prima di ricevere mi fa paura"),
    ('P03', COMPRA,  "Non capisco perche' lo stesso prodotto costa diverso"),
    ('P04', COMPRA,  "Gli sconti sembrano finti, non so mai il prezzo vero"),
    ('P05', COMPRA,  "Mi mettono fretta e decido di pancia"),
    ('P06', COMPRA,  "Se qualcosa va storto non rivedo i miei soldi"),
    ('P07', COMPRA,  "Non so se il prodotto e' buono o solo ben fotografato"),
    ('P08', COMPRA,  "Compro e dopo tre giorni mi pento"),
    ('P09', COMPRA,  "Mi sento tirchio a cercare il prezzo giusto"),
    ('P10', COMPRA,  "Il prezzo che vedo dipende da chi sono"),
    ('P11', PRODUCE, "Produco e mi resta invenduto in magazzino"),
    ('P12', PRODUCE, "A fine stagione devo svendere quello che ho fatto bene"),
    ('P13', PRODUCE, "Anticipo soldi senza sapere se vendero'"),
    ('P14', PRODUCE, "Per farmi vedere devo pagare qualcuno"),
]

# rubrica: (nome, angoli ammessi, destinatari ammessi, seme)
RUBRICHE = {
    'R1': ("Il conto in 10 secondi", {'dimostrazione', 'confronto'}, {COMPRA, PRODUCE, 'chi non ci conosce'},
           "un numero solo che si muove e chiude il discorso"),
    'R2': ("Traduzione simultanea", {'provocazione', 'confronto'}, {COMPRA, PRODUCE, 'chi non ci conosce'},
           "la frase che ti dicono tutti, e sotto cosa vuol dire davvero"),
    'R3': ("Domande vere", {'obiezione', 'dimostrazione', 'provocazione'}, {COMPRA, PRODUCE},
           "la domanda scomoda che nessuno fa ad alta voce"),
    'R4': ("Non e' colpa tua", {'provocazione', 'obiezione'}, {COMPRA, 'chi non ci conosce'},
           "ti hanno fatto sentire in colpa per la cosa sbagliata"),
    'R5': ("Dietro il prezzo pieno", {'dimostrazione', 'confronto', 'provocazione'}, {COMPRA, PRODUCE, 'chi non ci conosce'},
           "il prezzo smontato pezzo per pezzo, si vede da dove nasce"),
    'R6': ("Lo schermo non mente", {'dimostrazione', 'confronto', 'obiezione'}, {COMPRA, PRODUCE},
           "niente parole: si registra lo schermo e si guarda succedere"),
    'R7': ("Cosa firma un brand", {'dimostrazione', 'obiezione', 'confronto'}, {PRODUCE},
           "cosa cambia davvero nel mestiere di chi produce"),
    'R8': ("Si dice che", {'provocazione', 'confronto', 'obiezione'},
           {COMPRA, PRODUCE, 'chi non ci conosce'},
           "il detto che tutti ripetono, e dove smette di essere vero"),
}

ANGOLI = ['dimostrazione', 'obiezione', 'confronto', 'provocazione']

# rubriche escluse per lato del problema
ESCLUSE = {COMPRA: {'R7'}, PRODUCE: {'R4'}}

MAX_PER_COPPIA = 2   # stessa coppia problema+rubrica: al massimo 2 angoli, se no si ripete


def costruisci():
    combos, per_coppia = [], {}
    for pid, lato, testo in PROBLEMI:
        for rid, (nome, angoli_ok, dest_ok, seme) in RUBRICHE.items():
            if rid in ESCLUSE[lato]:
                continue
            if lato not in dest_ok:
                continue
            destinatari = [lato] + (['chi non ci conosce'] if 'chi non ci conosce' in dest_ok else [])
            for dest in destinatari:
                for ang in ANGOLI:
                    if ang not in angoli_ok:
                        continue
                    k = (pid, rid, dest)
                    if per_coppia.get(k, 0) >= MAX_PER_COPPIA:
                        continue
                    per_coppia[k] = per_coppia.get(k, 0) + 1
                    combos.append({
                        'id': f"{len(combos)+1:03d}",
                        'problema': pid, 'problema_testo': testo,
                        'rubrica': rid, 'rubrica_nome': nome,
                        'angolo': ang, 'destinatario': dest,
                        'seme': seme,
                        'stato': 'libero', 'post': None, 'data': None,
                    })
    return combos


def carica():
    return json.load(io.open(FILE, encoding='utf-8'))


def salva(d):
    io.open(FILE, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))


def init():
    c = costruisci()
    grezze = len(PROBLEMI) * len(RUBRICHE) * len(ANGOLI) * 2
    salva({'problemi': [{'id': i, 'lato': l, 'testo': t} for i, l, t in PROBLEMI],
           'rubriche': {k: v[0] for k, v in RUBRICHE.items()},
           'angoli': ANGOLI, 'combinazioni': c})
    print(f"{grezze} combinazioni grezze -> {len(c)} superstiti dopo il filtro "
          f"({100 - round(len(c)/grezze*100)}% scartate)")


def liberi():
    for c in carica()['combinazioni']:
        if c['stato'] == 'libero':
            print(f"{c['id']}\t{c['rubrica_nome']}\t{c['angolo']}\t{c['destinatario']}\t{c['seme']}")


def usa(cid, post, data):
    d = carica()
    for c in d['combinazioni']:
        if c['id'] == cid:
            c.update(stato='prodotto', post=post, data=data)
            salva(d); print(f"{cid} -> {post}"); return
    sys.exit(f'combinazione {cid} inesistente')


COL = {'dimostrazione': '#22c55e', 'obiezione': '#4a9eff',
       'confronto': '#a78bfa', 'provocazione': '#fbbf24'}


def dashboard():
    d = carica()
    c = d['combinazioni']
    per_rubrica = {}
    for x in c:
        per_rubrica.setdefault(x['rubrica'], []).append(x)
    liberi_n = sum(1 for x in c if x['stato'] == 'libero')

    sez = []
    for rid in sorted(per_rubrica):
        righe = ''.join(
            f'<tr class="{x["stato"]}"><td class="n">{x["id"]}</td>'
            f'<td><b>{html.escape(x["problema_testo"])}</b>'
            f'<span class="p">{html.escape(x["problema"])} &rarr; {html.escape(x["seme"])}</span></td>'
            f'<td><span class="a" style="--c:{COL[x["angolo"]]}">{x["angolo"]}</span></td>'
            f'<td class="d">{html.escape(x["destinatario"])}</td>'
            f'<td class="s">{"" if x["stato"]=="libero" else html.escape(x["post"] or x["stato"])}</td></tr>'
            for x in per_rubrica[rid])
        sez.append(f'<h2>{rid} · {html.escape(d["rubriche"][rid])} '
                   f'<span class="c">{len(per_rubrica[rid])}</span></h2>'
                   f'<table>{righe}</table>')

    doc = f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Griglia dei reel · Accumunation</title><style>
:root{{--bg:#0b1220;--card:#162038;--ink:#f0f4ff;--ink2:#8fa8c8;--ink3:#546880;--line:#243352}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);padding:32px 24px 80px;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}}
h1{{font-size:1.9rem;margin:0 0 .3rem;letter-spacing:-.02em}}
.sub{{color:var(--ink2);font-size:.95rem;max-width:74ch;line-height:1.55;margin:0 0 1.4rem}}
.chips{{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:2rem}}
.chip{{background:var(--card);border:1px solid var(--line);border-radius:999px;
padding:.35rem .85rem;font-size:.8rem;color:var(--ink2)}}
.chip b{{color:var(--ink)}}
h2{{font-size:1.05rem;margin:2rem 0 .7rem;font-weight:800}}
h2 .c{{font-size:.72rem;color:var(--ink3);font-weight:600;margin-left:.4rem}}
table{{width:100%;border-collapse:separate;border-spacing:0 4px}}
td{{background:var(--card);border-top:1px solid var(--line);border-bottom:1px solid var(--line);
padding:.6rem .7rem;font-size:.85rem;vertical-align:top}}
td:first-child{{border-left:1px solid var(--line);border-radius:10px 0 0 10px;width:46px}}
td:last-child{{border-right:1px solid var(--line);border-radius:0 10px 10px 0;width:150px}}
.n{{color:var(--ink3);font-size:.7rem}}
td b{{display:block;font-weight:600;line-height:1.4}}
.p{{display:block;margin-top:.3rem;font-size:.72rem;color:var(--ink3)}}
.a{{display:inline-block;font-size:.7rem;font-weight:800;letter-spacing:.04em;
color:var(--c);border:1px solid color-mix(in srgb,var(--c) 40%,transparent);
border-radius:999px;padding:.15rem .55rem;white-space:nowrap}}
.d{{color:var(--ink2);font-size:.78rem;white-space:nowrap;width:130px}}
.s{{color:var(--ink3);font-size:.72rem}}
tr.prodotto td{{opacity:.45}}
</style></head><body>
<h1>Griglia dei reel</h1>
<p class="sub">Quattro fattori: <b>problema</b> di chi guarda, <b>rubrica</b>, <b>angolo</b>, <b>destinatario</b>.
Il numero grezzo sarebbe molto piu' alto: quello che conta e' il filtro, che scarta le combinazioni
in cui la rubrica e l'angolo si contraddicono o il destinatario non c'entra. Ogni riga e' un reel
possibile, il seme e' la direzione, non il testo finale.</p>
<div class="chips">
  <span class="chip">combinazioni <b>{len(c)}</b></span>
  <span class="chip">libere <b>{liberi_n}</b></span>
  <span class="chip">problemi <b>{len(d['problemi'])}</b></span>
  <span class="chip">rubriche <b>{len(d['rubriche'])}</b></span>
</div>
{''.join(sez)}
</body></html>"""
    io.open(DASH, 'w', encoding='utf-8').write(doc)
    print(f'griglia-reel.html: {len(c)} combinazioni, {liberi_n} libere')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'dashboard'
    if cmd == 'init':
        init(); dashboard()
    elif cmd == 'liberi':
        liberi()
    elif cmd == 'usa':
        usa(*sys.argv[2:]); dashboard()
    else:
        dashboard()

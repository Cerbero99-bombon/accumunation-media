#!/usr/bin/env python3
"""Costruisce temi.json (registro dei 100 temi con stato) e rigenera la dashboard
griglia-contenuti.html marcando i temi gia' usati.

USO
  python3 temi.py init        # prima costruzione da raw.json (solo una volta)
  python3 temi.py usa 056 04-c-selezione-brand carosello 2026-07-30
  python3 temi.py dashboard   # rigenera l'HTML da temi.json
  python3 temi.py liberi      # elenca i temi ancora liberi, per gli agenti

Stati: libero -> assegnato (un agente ci sta lavorando) -> prodotto (file pronti,
in coda) -> pubblicato (uscito davvero).
"""
import json, sys, io, os, html

QUI = os.path.dirname(os.path.abspath(__file__))
TEMI = os.path.join(QUI, 'temi.json')
DASH = os.path.join(QUI, 'griglia-contenuti.html')

STATI = ['libero', 'assegnato', 'prodotto', 'pubblicato']


def carica():
    return json.load(io.open(TEMI, encoding='utf-8'))


def salva(d):
    io.open(TEMI, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))


def init(raw_path):
    r = json.load(io.open(raw_path, encoding='utf-8'))
    temi = [{'id': i, 'riga': ri, 'colonna': co, 'tema': te,
             'stato': 'libero', 'post': None, 'formato': None, 'data': None}
            for i, ri, co, te in r['t']]
    salva({'vantaggi': r['v'], 'temi': temi})
    print(f'temi.json creato con {len(temi)} temi')


def usa(tid, post, formato, data, stato='pubblicato'):
    d = carica()
    for t in d['temi']:
        if t['id'] == tid:
            t.update(stato=stato, post=post, formato=formato, data=data)
            salva(d)
            print(f"{tid} -> {stato} ({post}, {formato}, {data})")
            return
    sys.exit(f'tema {tid} inesistente')


def liberi():
    d = carica()
    for t in d['temi']:
        if t['stato'] == 'libero':
            print(f"{t['id']}\t{t['riga']} -> {t['colonna']}\t{t['tema']}")


COLORI = {'libero': '#162038', 'assegnato': '#3a2f12', 'prodotto': '#123049', 'pubblicato': '#0f3324'}
BORDI = {'libero': '#243352', 'assegnato': '#8a6a1e', 'prodotto': '#1d5fae', 'pubblicato': '#22c55e'}


def dashboard():
    d = carica()
    v = d['vantaggi']
    per_cella = {(t['riga'], t['colonna']): t for t in d['temi']}
    conta = {s: sum(1 for t in d['temi'] if t['stato'] == s) for s in STATI}

    celle = []
    for ri in v:
        riga = [f'<th scope="row">{html.escape(ri)}</th>']
        for co in v:
            t = per_cella[(ri, co)]
            st = t['stato']
            meta = ''
            if t['post']:
                meta = f"<em>{html.escape(t['formato'] or '')} · {html.escape(t['data'] or '')}</em>"
            riga.append(
                f'<td class="c {st}" data-stato="{st}" title="{html.escape(ri)} letto attraverso {html.escape(co)}">'
                f'<span class="n">{t["id"]}</span>'
                f'<span class="t">{html.escape(t["tema"])}</span>{meta}</td>')
        celle.append('<tr>' + ''.join(riga) + '</tr>')

    intest = ''.join(f'<th class="col">{html.escape(c)}</th>' for c in v)
    doc = f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Griglia dei contenuti · Accumunation</title><style>
:root{{--bg:#0b1220;--bg2:#0f1a2e;--card:#162038;--ink:#f0f4ff;--ink2:#8fa8c8;--ink3:#546880;
--verde:#22c55e;--blu:#4a9eff;--line:#243352}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
padding:32px 24px 64px}}
h1{{font-size:1.9rem;margin:0 0 .4rem;letter-spacing:-.02em}}
.sub{{color:var(--ink2);max-width:70ch;line-height:1.55;margin:0 0 1.6rem;font-size:.95rem}}
.legenda{{display:flex;gap:.6rem;flex-wrap:wrap;margin:0 0 1.4rem}}
.chip{{display:inline-flex;align-items:center;gap:.45rem;background:var(--card);
border:1px solid var(--line);border-radius:999px;padding:.35rem .8rem;font-size:.82rem;color:var(--ink2)}}
.chip b{{color:var(--ink);font-variant-numeric:tabular-nums}}
.dot{{width:9px;height:9px;border-radius:50%}}
table{{border-collapse:separate;border-spacing:4px;width:100%;table-layout:fixed}}
th{{font-size:.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
color:var(--ink3);text-align:left;vertical-align:bottom;padding:0 .3rem .4rem}}
th[scope=row]{{width:104px;vertical-align:middle;text-align:right;padding-right:.6rem}}
td.c{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.6rem .65rem;
vertical-align:top;font-size:.79rem;line-height:1.35;position:relative;min-height:86px}}
td .n{{display:block;font-size:.62rem;color:var(--ink3);letter-spacing:.08em;margin-bottom:.25rem}}
td .t{{display:block;color:var(--ink)}}
td em{{display:block;margin-top:.4rem;font-style:normal;font-size:.68rem;color:var(--ink3)}}
td.pubblicato{{background:{COLORI['pubblicato']};border-color:{BORDI['pubblicato']}}}
td.pubblicato .t{{color:var(--ink2);text-decoration:line-through;text-decoration-color:var(--ink3)}}
td.prodotto{{background:{COLORI['prodotto']};border-color:{BORDI['prodotto']}}}
td.assegnato{{background:{COLORI['assegnato']};border-color:{BORDI['assegnato']}}}
.nota{{color:var(--ink3);font-size:.8rem;margin-top:1.8rem;border-top:1px solid var(--line);padding-top:1rem}}
@media(max-width:1100px){{body{{padding:20px 12px}}td.c{{font-size:.72rem}}th[scope=row]{{width:76px;font-size:.62rem}}}}
</style></head><body>
<h1>Griglia dei contenuti</h1>
<p class="sub">Dieci vantaggi incrociati fra loro, 100 caselle, 100 temi. Si legge per riga: il vantaggio
della riga e' il protagonista del post, quello della colonna e' la lente con cui lo si guarda.
La griglia non e' simmetrica: sopra e sotto la diagonale sono due post diversi sullo stesso incrocio.
Questa pagina si rigenera da <code>temi.json</code>: non va modificata a mano.</p>
<div class="legenda">
  <span class="chip"><span class="dot" style="background:{BORDI['libero']}"></span>liberi <b>{conta['libero']}</b></span>
  <span class="chip"><span class="dot" style="background:{BORDI['assegnato']}"></span>in lavorazione <b>{conta['assegnato']}</b></span>
  <span class="chip"><span class="dot" style="background:{BORDI['prodotto']}"></span>pronti in coda <b>{conta['prodotto']}</b></span>
  <span class="chip"><span class="dot" style="background:{BORDI['pubblicato']}"></span>pubblicati <b>{conta['pubblicato']}</b></span>
</div>
<table><tr><th></th>{intest}</tr>{''.join(celle)}</table>
<p class="nota">Accumunation &middot; la lista dei vantaggi vive in <code>temi.json</code>: cambiala li' e la griglia si rigenera.</p>
</body></html>"""
    io.open(DASH, 'w', encoding='utf-8').write(doc)
    print(f'dashboard rigenerata: {conta}')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'dashboard'
    if cmd == 'init':
        init(sys.argv[2] if len(sys.argv) > 2 else os.path.join(QUI, 'raw.json'))
        dashboard()
    elif cmd == 'usa':
        usa(*sys.argv[2:])
        dashboard()
    elif cmd == 'liberi':
        liberi()
    else:
        dashboard()

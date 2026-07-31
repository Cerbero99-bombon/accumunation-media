#!/usr/bin/env python3
"""Archivio delle idee e delle cose in mano a Enrico.

Esiste per una ragione sola: Enrico dice cose intelligenti dentro discorsi su altro,
e quelle cose si perdono. Qui non si perdono. E quando arriva il momento giusto,
ricompaiono da sole.

USO
  python3 piano/idee.py aggiungi --tipo idea --titolo "..." --dettaglio "..." \
      --quando "prima campagna" --area reel
  python3 piano/idee.py aggiungi --tipo enrico --titolo "..." --scadenza 2026-08-05
  python3 piano/idee.py mature            # cosa e' il momento di ripescare, adesso
  python3 piano/idee.py fatto <id>
  python3 piano/idee.py stato <id> <nuovo-stato>
  python3 piano/idee.py dashboard         # rigenera piano/plancia.html

TIPI
  idea    una visione, un'intuizione, una direzione. Non ha una scadenza, ha un momento.
  enrico  una cosa che deve fare lui a mano. Ha una scadenza e va ricordata.

QUANDO (il momento in cui l'idea torna a galla)
  subito · prima campagna · primi 500 follower · primo brand confermato ·
  quando un reel supera 1000 views · fra un mese · da valutare
"""
import json, io, os, sys, argparse, datetime

QUI = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(QUI, 'idee.json')
DASH = os.path.join(QUI, 'plancia.html')

STATI = ['aperta', 'in corso', 'fatta', 'scartata']


def carica():
    if not os.path.exists(FILE):
        return {'voci': []}
    return json.load(io.open(FILE, encoding='utf-8'))


def salva(d):
    io.open(FILE, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))


def nuovo_id(d):
    return f"{len(d['voci']) + 1:03d}"


def aggiungi(a):
    d = carica()
    v = {'id': nuovo_id(d), 'tipo': a.tipo, 'titolo': a.titolo,
         'dettaglio': a.dettaglio or '', 'area': a.area or '',
         'quando': a.quando or 'da valutare', 'scadenza': a.scadenza or None,
         'stato': 'aperta', 'nata': a.nata or 'conversazione'}
    d['voci'].append(v)
    salva(d)
    print(f"{v['id']} · {v['tipo']} · {v['titolo']}")


def mature(oggi=None):
    """Cosa va rimesso davanti a Enrico adesso."""
    oggi = oggi or datetime.date.today()
    d = carica()
    fuori = []
    for v in d['voci']:
        if v['stato'] in ('fatta', 'scartata'):
            continue
        if v['tipo'] == 'enrico':
            fuori.append(v)          # le sue cose si ricordano sempre finche' non sono fatte
        elif v['quando'] == 'subito':
            fuori.append(v)
        elif v.get('scadenza'):
            try:
                if datetime.date.fromisoformat(v['scadenza']) <= oggi + datetime.timedelta(days=7):
                    fuori.append(v)
            except ValueError:
                pass
    for v in fuori:
        sc = f" (entro {v['scadenza']})" if v.get('scadenza') else ''
        print(f"{v['id']}\t{v['tipo']}\t{v['titolo']}{sc}")
    return fuori


def stato(vid, nuovo):
    d = carica()
    for v in d['voci']:
        if v['id'] == vid:
            v['stato'] = nuovo
            salva(d)
            print(f"{vid} -> {nuovo}")
            return
    sys.exit(f'voce {vid} inesistente')


import html as _h


def dashboard():
    d = carica()
    oggi = datetime.date.today()
    idee = [v for v in d['voci'] if v['tipo'] == 'idea']
    cose = [v for v in d['voci'] if v['tipo'] == 'enrico']
    aperte = lambda L: [v for v in L if v['stato'] not in ('fatta', 'scartata')]

    def scheda(v):
        cls = v['stato'].replace(' ', '-')
        meta = []
        if v.get('area'):
            meta.append(_h.escape(v['area']))
        if v.get('quando') and v['tipo'] == 'idea':
            meta.append('torna: ' + _h.escape(v['quando']))
        if v.get('scadenza'):
            try:
                g = (datetime.date.fromisoformat(v['scadenza']) - oggi).days
                meta.append(f"entro {v['scadenza']}" + (f" · {g} giorni" if g >= 0 else " · SCADUTA"))
            except ValueError:
                meta.append('entro ' + v['scadenza'])
        det = f"<p>{_h.escape(v['dettaglio'])}</p>" if v['dettaglio'] else ''
        return (f'<article class="v {cls}"><span class="n">{v["id"]}</span>'
                f'<h3>{_h.escape(v["titolo"])}</h3>{det}'
                f'<div class="meta">{" · ".join(meta)}</div></article>')

    doc = f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plancia · Accumunation</title><style>
:root{{--bg:#0b1220;--card:#162038;--ink:#f0f4ff;--ink2:#8fa8c8;--ink3:#546880;
--verde:#22c55e;--blu:#4a9eff;--ambra:#fbbf24;--line:#243352}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);padding:32px 24px 80px;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}}
h1{{font-size:1.9rem;margin:0 0 .3rem;letter-spacing:-.02em}}
.sub{{color:var(--ink2);font-size:.95rem;max-width:72ch;line-height:1.55;margin:0 0 2rem}}
h2{{font-size:1.05rem;margin:2.2rem 0 .9rem;letter-spacing:.04em;text-transform:uppercase;
color:var(--ink3);font-weight:800}}
h2:first-of-type{{margin-top:0}}
.griglia{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:.8rem}}
.v{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line);
border-radius:12px;padding:.9rem 1rem 1rem;position:relative}}
.v .n{{font-size:.62rem;color:var(--ink3);letter-spacing:.1em}}
.v h3{{font-size:.98rem;margin:.25rem 0 .45rem;line-height:1.35}}
.v p{{font-size:.83rem;color:var(--ink2);line-height:1.55;margin:0 0 .6rem}}
.v .meta{{font-size:.72rem;color:var(--ink3)}}
.v.aperta{{border-left-color:var(--blu)}}
.v.in-corso{{border-left-color:var(--ambra)}}
.v.fatta{{border-left-color:var(--verde);opacity:.5}}
.v.fatta h3{{text-decoration:line-through;text-decoration-color:var(--ink3)}}
.v.scartata{{opacity:.35}}
.vuoto{{color:var(--ink3);font-size:.9rem}}
</style></head><body>
<h1>Plancia</h1>
<p class="sub">Quello che hai detto e che non deve andare perso, e quello che resta in mano a te.
Le idee non hanno una scadenza, hanno un momento: ricompaiono quando quel momento arriva.
Questa pagina si rigenera da <code>idee.json</code>.</p>

<h2>Cose in mano a te &middot; {len(aperte(cose))} aperte</h2>
<div class="griglia">{''.join(scheda(v) for v in cose) or '<p class="vuoto">Niente in sospeso.</p>'}</div>

<h2>Idee e visioni &middot; {len(aperte(idee))} vive</h2>
<div class="griglia">{''.join(scheda(v) for v in idee) or '<p class="vuoto">Archivio vuoto.</p>'}</div>
</body></html>"""
    io.open(DASH, 'w', encoding='utf-8').write(doc)
    print(f'plancia.html: {len(aperte(cose))} cose per Enrico, {len(aperte(idee))} idee vive')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    a = sub.add_parser('aggiungi')
    a.add_argument('--tipo', choices=['idea', 'enrico'], required=True)
    a.add_argument('--titolo', required=True)
    a.add_argument('--dettaglio', default='')
    a.add_argument('--area', default='')
    a.add_argument('--quando', default='da valutare')
    a.add_argument('--scadenza', default=None)
    a.add_argument('--nata', default='conversazione')
    sub.add_parser('mature')
    s = sub.add_parser('stato'); s.add_argument('id'); s.add_argument('nuovo')
    f = sub.add_parser('fatto'); f.add_argument('id')
    sub.add_parser('dashboard')
    args = ap.parse_args()
    if args.cmd == 'aggiungi':
        aggiungi(args); dashboard()
    elif args.cmd == 'mature':
        mature()
    elif args.cmd == 'stato':
        stato(args.id, args.nuovo); dashboard()
    elif args.cmd == 'fatto':
        stato(args.id, 'fatta'); dashboard()
    else:
        dashboard()

#!/usr/bin/env python3
"""La dispensa: materiale vero da cui la fabbrica pesca.

Numeri, leggi, sanzioni e studi verificabili, con la fonte e il motivo per cui li teniamo.
Serve a una cosa sola: far si' che un contenuto Accumunation possa essere controllato da chiunque.
Ogni voce ha anche la sua **cautela**, cioe' come NON va usata.

USO
  python3 piano/dispensa.py init <seed.json>
  python3 piano/dispensa.py dashboard
  python3 piano/dispensa.py usa <id> <post>
"""
import json, io, os, sys, html

QUI = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(QUI, 'dispensa.json')
DASH = os.path.join(QUI, 'dispensa.html')

FORZA = {
    'legge':    ('#22c55e', 'legge'),
    'sentenza': ('#22c55e', 'sentenza'),
    'sanzione': ('#22c55e', 'sanzione'),
    'ufficiale':('#4a9eff', 'ente ufficiale'),
    'bilancio': ('#4a9eff', 'bilancio'),
    'studio':   ('#a78bfa', 'studio'),
}


def carica():
    return json.load(io.open(FILE, encoding='utf-8'))


def salva(d):
    io.open(FILE, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))


def init(seed):
    d = json.load(io.open(seed, encoding='utf-8'))
    for v in d['voci']:
        v.setdefault('stato', 'libera')
        v.setdefault('post', None)
    salva(d)
    print(f"dispensa: {len(d['voci'])} voci, {len(d.get('scartate', []))} scartate con motivo")


def usa(vid, post):
    d = carica()
    for v in d['voci']:
        if v['id'] == vid:
            v.update(stato='usata', post=post); salva(d); print(f'{vid} -> {post}'); return
    sys.exit(f'voce {vid} inesistente')


def dashboard():
    d = carica()
    per_tema = {}
    for v in d['voci']:
        per_tema.setdefault(v['tema'], []).append(v)

    sez = []
    for tema in sorted(per_tema):
        blocchi = []
        for v in per_tema[tema]:
            col, et = FORZA.get(v['forza'], ('#546880', v['forza']))
            caut = (f'<p class="caut"><b>Attenzione:</b> {html.escape(v["cautela"])}</p>'
                    if v.get('cautela') else '')
            rub = ' '.join(f'<span class="r">{r}</span>' for r in v.get('rubriche', []))
            blocchi.append(f"""<article class="v {v.get('stato','libera')}">
 <div class="top"><span class="id">{v['id']}</span>
   <span class="f" style="--c:{col}">{et}</span>{rub}</div>
 <h3>{html.escape(v['titolo'])}</h3>
 <p class="dato">{html.escape(v['dato'])}</p>
 <p class="perche">{html.escape(v['perche'])}</p>
 {caut}
 <a class="fonte" href="{html.escape(v['url'])}" target="_blank" rel="noopener">{html.escape(v['fonte'])}</a>
</article>""")
        sez.append(f'<h2>{html.escape(tema)} <span class="c">{len(per_tema[tema])}</span></h2>'
                   f'<div class="griglia">{"".join(blocchi)}</div>')

    scart = ''.join(
        f'<article class="sc"><h3>{html.escape(s["cosa"])}</h3><p>{html.escape(s["perche"])}</p></article>'
        for s in d.get('scartate', []))

    doc = f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dispensa · Accumunation</title><style>
:root{{--bg:#0b1220;--card:#162038;--ink:#f0f4ff;--ink2:#8fa8c8;--ink3:#546880;--line:#243352}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);padding:32px 24px 80px;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}}
h1{{font-size:1.9rem;margin:0 0 .3rem;letter-spacing:-.02em}}
.sub{{color:var(--ink2);font-size:.95rem;max-width:74ch;line-height:1.55;margin:0 0 2rem}}
h2{{font-size:.95rem;margin:2.2rem 0 .8rem;text-transform:uppercase;letter-spacing:.08em;
color:var(--ink3);font-weight:800}}
h2 .c{{color:var(--ink3);font-weight:600}}
.griglia{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:.8rem}}
.v{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:1rem 1.1rem 1.1rem}}
.top{{display:flex;align-items:center;gap:.45rem;flex-wrap:wrap;margin-bottom:.5rem}}
.id{{font-size:.65rem;color:var(--ink3);letter-spacing:.08em}}
.f{{font-size:.65rem;font-weight:800;letter-spacing:.05em;color:var(--c);
border:1px solid color-mix(in srgb,var(--c) 40%,transparent);border-radius:999px;padding:.12rem .5rem}}
.r{{font-size:.62rem;color:var(--ink3);border:1px solid var(--line);border-radius:999px;padding:.12rem .4rem}}
.v h3{{font-size:1rem;margin:0 0 .45rem;line-height:1.35}}
.dato{{font-size:.82rem;color:var(--ink2);margin:0 0 .6rem;font-variant-numeric:tabular-nums}}
.perche{{font-size:.82rem;color:var(--ink);margin:0 0 .6rem;line-height:1.5;
border-left:2px solid #22c55e;padding-left:.7rem}}
.caut{{font-size:.76rem;color:#fbbf24;margin:0 0 .6rem;line-height:1.45}}
.caut b{{color:#fbbf24}}
.fonte{{font-size:.72rem;color:var(--ink3);text-decoration:none;border-bottom:1px solid var(--line)}}
.fonte:hover{{color:var(--ink2)}}
.v.usata{{opacity:.45}}
.sc{{background:transparent;border:1px dashed var(--line);border-radius:12px;padding:.8rem 1rem;margin-bottom:.6rem}}
.sc h3{{font-size:.9rem;margin:0 0 .35rem;color:var(--ink2)}}
.sc p{{font-size:.8rem;color:var(--ink3);margin:0;line-height:1.5}}
</style></head><body>
<h1>Dispensa</h1>
<p class="sub">Materiale vero da cui la fabbrica pesca: numeri, leggi, sanzioni e studi che chiunque
puo' andare a verificare. Ogni voce dice <b>perche' la teniamo</b> e, quando serve, <b>come non va
usata</b>. Un contenuto che poggia su una di queste voci non e' un'opinione nostra: e' un fatto con
un indirizzo.</p>
{''.join(sez)}
<h2>Scartate, e perche'</h2>
{scart}
</body></html>"""
    io.open(DASH, 'w', encoding='utf-8').write(doc)
    print(f'dispensa.html: {len(d["voci"])} voci, {len(d.get("scartate", []))} scartate')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'dashboard'
    if cmd == 'init':
        init(sys.argv[2]); dashboard()
    elif cmd == 'usa':
        usa(sys.argv[2], sys.argv[3]); dashboard()
    else:
        dashboard()

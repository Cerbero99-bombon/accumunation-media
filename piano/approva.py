#!/usr/bin/env python3
"""Genera piano/da-approvare.html: tutto quello che e' in coda e non ancora uscito,
con le immagini vere, la caption e la data. E' la pagina che Enrico apre per approvare.

USO: python3 piano/approva.py     (dalla radice del repo accumunation-media)
"""
import json, io, os, html, datetime

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
QUEUE = os.path.join(RADICE, 'queue.json')
TEMI = os.path.join(QUI, 'temi.json')
OUT = os.path.join(QUI, 'da-approvare.html')

ICONA = {'carosello': 'CAROSELLO', 'reel': 'REEL', 'storia': 'STORIA', 'threads': 'THREADS'}


def main():
    q = json.load(io.open(QUEUE, encoding='utf-8'))
    temi = {}
    if os.path.exists(TEMI):
        for t in json.load(io.open(TEMI, encoding='utf-8'))['temi']:
            if t.get('post'):
                temi.setdefault(t['post'], []).append(f"{t['id']} · {t['tema']}")

    voci = [p for p in q['post'] if not p.get('pubblicato')]
    voci.sort(key=lambda p: p.get('quando', ''))

    if voci:
        ultima = voci[-1]['quando'][:10]
        try:
            giorni = (datetime.date.fromisoformat(ultima) - datetime.date.today()).days
        except ValueError:
            giorni = '?'
    else:
        ultima, giorni = '—', 0

    schede = []
    for p in voci:
        media = p.get('media') or []
        img = ''.join(
            f'<a class="sh" href="{html.escape(u)}" target="_blank" rel="noopener">'
            f'<img loading="lazy" src="{html.escape(u)}" alt=""></a>'
            for u in media if not u.lower().endswith(('.mp4', '.mov')))
        vid = ''.join(
            f'<video class="sh" controls preload="none" src="{html.escape(u)}"></video>'
            for u in media if u.lower().endswith(('.mp4', '.mov')))
        cap = html.escape(p.get('caption', '')).replace('\n', '<br>')
        orig = temi.get(p['id'])
        schede.append(f"""<article class="post">
  <header>
    <span class="tipo">{ICONA.get(p.get('tipo'), (p.get('tipo') or '').upper())}</span>
    <h2>{html.escape(p.get('titolo') or p['id'])}</h2>
    <span class="quando">{html.escape(p.get('quando', ''))}</span>
  </header>
  <div class="strip">{img}{vid}</div>
  <div class="cap">{cap}</div>
  {f'<div class="orig">dalla griglia: {html.escape(" / ".join(orig))}</div>' if orig else ''}
</article>""")

    doc = f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Da approvare · Accumunation</title><style>
:root{{--bg:#0b1220;--card:#162038;--ink:#f0f4ff;--ink2:#8fa8c8;--ink3:#546880;
--verde:#22c55e;--blu:#4a9eff;--line:#243352}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);padding:32px 24px 80px;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}}
h1{{font-size:1.9rem;margin:0 0 .3rem;letter-spacing:-.02em}}
.sub{{color:var(--ink2);font-size:.95rem;max-width:70ch;line-height:1.55;margin:0 0 1.4rem}}
.riepilogo{{display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:2rem}}
.chip{{background:var(--card);border:1px solid var(--line);border-radius:999px;
padding:.4rem .9rem;font-size:.83rem;color:var(--ink2)}}
.chip b{{color:var(--ink)}}
.chip.allarme{{border-color:#b45309;color:#fbbf24}}
.post{{background:var(--card);border:1px solid var(--line);border-radius:16px;
padding:1.1rem 1.2rem 1.3rem;margin-bottom:1.1rem}}
.post header{{display:flex;align-items:baseline;gap:.8rem;flex-wrap:wrap;margin-bottom:.9rem}}
.tipo{{font-size:.66rem;font-weight:800;letter-spacing:.12em;color:var(--verde);
border:1px solid rgba(34,197,94,.35);border-radius:999px;padding:.2rem .6rem}}
.post h2{{font-size:1.12rem;margin:0;flex:1;min-width:200px}}
.quando{{font-size:.8rem;color:var(--ink3);font-variant-numeric:tabular-nums}}
.strip{{display:flex;gap:.5rem;overflow-x:auto;padding-bottom:.5rem;margin-bottom:.9rem}}
.sh{{flex:0 0 auto;width:176px;border-radius:10px;overflow:hidden;background:#0b1220;
border:1px solid var(--line);display:block}}
.sh img,.sh video{{display:block;width:100%;height:auto}}
video.sh{{width:176px}}
.cap{{font-size:.88rem;line-height:1.6;color:var(--ink2);white-space:normal;
border-left:2px solid var(--line);padding-left:.9rem}}
.orig{{margin-top:.8rem;font-size:.74rem;color:var(--ink3)}}
.vuoto{{color:var(--ink3);font-size:.95rem}}
</style></head><body>
<h1>Da approvare</h1>
<p class="sub">Tutto quello che uscira' e non e' ancora uscito. Guardalo qui in una volta sola:
se non dici niente esce cosi' com'e'. Se una cosa non va, dimmi quale post e cosa cambiare.</p>
<div class="riepilogo">
  <span class="chip">in coda <b>{len(voci)}</b></span>
  <span class="chip">copertura fino al <b>{ultima}</b></span>
  <span class="chip{' allarme' if isinstance(giorni, int) and giorni < 30 else ''}">margine <b>{giorni} giorni</b>{' · sotto i 30, si produce' if isinstance(giorni, int) and giorni < 30 else ''}</span>
</div>
{''.join(schede) if schede else '<p class="vuoto">Coda vuota.</p>'}
</body></html>"""
    io.open(OUT, 'w', encoding='utf-8').write(doc)
    print(f'da-approvare.html: {len(voci)} contenuti, copertura {giorni} giorni (fino al {ultima})')


if __name__ == '__main__':
    main()

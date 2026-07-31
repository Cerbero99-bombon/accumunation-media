#!/usr/bin/env python3
"""Stile B — 'Numeri vivi'. Il protagonista e' un numero che si muove, non il testo.

Costruisce la pagina HTML animata e la pilota con setT(t) da Playwright, un fotogramma
alla volta. Deterministico: stesso input, stesso video, sempre.
"""
import json, base64, pathlib, sys

QUI = pathlib.Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30


def logo_uri(p):
    return "data:image/png;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def fonts_css(root):
    root = pathlib.Path(root)
    out = []
    for fam, pkg, pesi in [("Manrope", "manrope", [400, 600, 800]),
                           ("Space Grotesk", "space-grotesk", [500, 700])]:
        for w in pesi:
            f = root / f"{pkg}-latin-{w}-normal.woff2"
            if not f.is_file():
                continue
            b = base64.b64encode(f.read_bytes()).decode()
            out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-display:block;"
                       f"src:url(data:font/woff2;base64,{b}) format('woff2')}}")
    return "".join(out)


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden}
body{background:#0b1220;color:#f0f4ff;font-family:'Manrope',sans-serif;position:relative}
.glow{position:absolute;width:1200px;height:1200px;border-radius:50%;
 background:radial-gradient(circle,rgba(34,197,94,.13),transparent 62%);top:-380px;right:-420px}
.glow2{position:absolute;width:1100px;height:1100px;border-radius:50%;
 background:radial-gradient(circle,rgba(74,158,255,.10),transparent 62%);bottom:-420px;left:-380px}
header{position:absolute;top:74px;left:88px;right:88px;display:flex;align-items:center;gap:18px;z-index:5}
header img{height:64px;width:auto;display:block}
header span{font-family:'Space Grotesk';font-weight:700;font-size:34px;letter-spacing:-.5px}
main{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;
 align-items:flex-start;padding:0 88px;z-index:4}
.scena{position:absolute;left:88px;right:88px;top:50%;transform:translateY(-50%);
 display:flex;flex-direction:column;align-items:flex-start;gap:26px;opacity:0}
.kick{font-family:'Space Grotesk';font-weight:700;font-size:30px;letter-spacing:.16em;
 text-transform:uppercase;color:#22c55e}
h1{font-family:'Space Grotesk';font-weight:700;font-size:104px;line-height:1.02;letter-spacing:-3px}
h1 em{font-style:normal;color:#22c55e}
h1.sm{font-size:78px}
.sub{font-size:40px;line-height:1.35;color:#8fa8c8;max-width:820px}
/* il numero protagonista */
.num{font-family:'Space Grotesk';font-weight:700;font-size:280px;line-height:.95;
 letter-spacing:-12px;font-variant-numeric:tabular-nums;color:#f0f4ff;white-space:nowrap}
.num.verde{color:#22c55e}
.num small{font-size:.42em;letter-spacing:-4px}
.barra{width:100%;height:22px;border-radius:11px;background:#162038;overflow:hidden;
 border:1px solid #243352}
.barra i{display:block;height:100%;background:linear-gradient(90deg,#22c55e,#4ade80);width:0}
.prezzo{font-family:'Space Grotesk';font-weight:700;font-size:190px;letter-spacing:-8px;
 position:relative;display:inline-block;color:#546880;white-space:nowrap}
.prezzo .taglio{position:absolute;left:-18px;top:50%;height:16px;border-radius:8px;
 background:#ef4444;width:0;box-shadow:0 0 24px rgba(239,68,68,.5)}
/* sottotitoli bruciati */
.st{position:absolute;left:88px;right:88px;bottom:280px;text-align:center;z-index:6;
 font-family:'Space Grotesk';font-weight:700;font-size:62px;line-height:1.15;letter-spacing:-1px}
.st b{font-weight:700;color:#f0f4ff}
.st b.on{color:#22c55e}
footer{position:absolute;left:88px;right:88px;bottom:88px;display:flex;justify-content:space-between;
 align-items:center;font-size:26px;color:#546880;z-index:5}
footer .site{font-weight:600}
.fonte{position:absolute;left:88px;right:88px;bottom:150px;font-size:24px;color:#546880;z-index:5;opacity:0}
"""

JS = """
const SC = __SCENE__, WD = __WORDS__, DUR = __DUR__;
window.TOT = DUR;
function ease(x){return x<0?0:x>1?1:1-Math.pow(1-x,3);}
function setT(t){
  // scene
  document.querySelectorAll('.scena').forEach((el,i)=>{
    const s=SC[i]; let o=0;
    if(t>=s.a-0.16 && t<=s.b+0.16){
      const fi=Math.min(1,(t-(s.a-0.16))/0.16), fo=Math.min(1,((s.b+0.16)-t)/0.16);
      o=Math.min(fi,fo);
    }
    el.style.opacity=o.toFixed(3);
    el.style.transform='translateY(-50%) translateY('+((1-o)*18).toFixed(1)+'px)';
  });
  // contatori
  document.querySelectorAll('[data-count]').forEach(n=>{
    const s=SC[+n.dataset.scene], p=ease((t-s.a)/Math.max(.01,(s.b-s.a)*0.55));
    const v=Math.round(p*(+n.dataset.count));
    n.firstChild.nodeValue=v.toLocaleString('it-IT');});
  document.querySelectorAll('[data-bar]').forEach(b=>{
    const s=SC[+b.dataset.scene], p=ease((t-s.a)/Math.max(.01,(s.b-s.a)*0.55));
    b.style.width=(p*(+b.dataset.bar))+'%';});
  document.querySelectorAll('[data-cut]').forEach(c=>{
    const s=SC[+c.dataset.scene], p=ease((t-(s.a+0.45))/0.45);
    c.style.width=(p*(c.parentElement.offsetWidth+36))+'px';});
  // sottotitoli: la parola corrente in verde
  const st=document.querySelector('.st'); let html='', found=-1;
  for(let i=0;i<WD.length;i++){ if(t>=WD[i][0]&&t<=WD[i][1]){found=i;break;} }
  if(found<0){ for(let i=WD.length-1;i>=0;i--){ if(t>WD[i][1]&&t-WD[i][1]<0.95){found=i;break;} } }
  if(found>=0){
    const g=WD[found][3];
    for(let i=0;i<WD.length;i++) if(WD[i][3]===g)
      html+='<b class="'+(i===found?'on':'')+'">'+WD[i][2]+'</b> ';
  }
  st.innerHTML=html;
  // riga fonte
  const f=document.querySelector('.fonte');
  f.style.opacity = (t>__FONTE__) ? '1' : '0';
}
setT(0);
"""


def build(spec):
    scene, corpi = spec["scene"], []
    for i, s in enumerate(scene):
        body = ""
        if s.get("kick"):
            body += f'<div class="kick">{s["kick"]}</div>'
        if s.get("prezzo"):
            body += (f'<div class="prezzo">{s["prezzo"]}'
                     f'<i class="taglio" data-cut data-scene="{i}"></i></div>')
        if s.get("count") is not None:
            st = f' style="font-size:{s["numsize"]}px"' if s.get("numsize") else ""
            body += (f'<div class="num verde"{st} data-count="{s["count"]}" data-scene="{i}">0'
                     f'<small>{s.get("suffisso","")}</small></div>')
        if s.get("bar") is not None:
            body += f'<div class="barra"><i data-bar="{s["bar"]}" data-scene="{i}"></i></div>'
        if s.get("h1"):
            cls = " sm" if s.get("piccolo") else ""
            body += f'<h1 class="{cls}">{s["h1"]}</h1>'
        if s.get("sub"):
            body += f'<p class="sub">{s["sub"]}</p>'
        corpi.append(f'<div class="scena">{body}</div>')

    js = (JS.replace("__SCENE__", json.dumps([{"a": s["a"], "b": s["b"]} for s in scene]))
            .replace("__WORDS__", json.dumps(spec["parole"], ensure_ascii=False))
            .replace("__DUR__", str(spec["durata"]))
            .replace("__FONTE__", str(spec.get("fonte_da", 1e9))))

    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<style>{spec['fonts']}{CSS}</style></head><body>
<div class="glow"></div><div class="glow2"></div>
<header><img src="{spec['logo']}" alt=""><span>Accumunation</span></header>
<main>{''.join(corpi)}</main>
<div class="st"></div>
<div class="fonte">{spec.get('fonte','')}</div>
<footer><span class="site">accumunation.it</span><span>{spec.get('swipe','')}</span></footer>
<script>{js}</script></body></html>"""


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    spec["fonts"] = fonts_css(spec["font_root"])
    spec["logo"] = logo_uri(spec["logo_path"])
    pathlib.Path(sys.argv[2]).write_text(build(spec), encoding="utf-8")
    print(sys.argv[2])

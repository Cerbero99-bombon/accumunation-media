#!/usr/bin/env python3
"""Reel a movimento continuo: una sola inquadratura, niente stacchi.

L'idea visiva e' il meccanismo stesso di Accumunation: le persone si accumulano dal basso e il
prezzo, appeso in alto, scende man mano che loro salgono. Non e' una sequenza di immagini con
una dissolvenza: e' una cosa sola che si muove per tutta la durata.

Il testo entra a parole, non a schermate. La camera fa una spinta lenta e costante.
"""
import json, base64, pathlib, sys

W, H = 1080, 1920


def logo_uri(p):
    return "data:image/png;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def fonts_css(root):
    root = pathlib.Path(root)
    out = []
    for fam, pkg, pesi in [("Manrope", "manrope", [400, 600, 800]),
                           ("Space Grotesk", "space-grotesk", [500, 700])]:
        for w in pesi:
            f = root / f"{pkg}-latin-{w}-normal.woff2"
            if f.is_file():
                b = base64.b64encode(f.read_bytes()).decode()
                out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-display:block;"
                           f"src:url(data:font/woff2;base64,{b}) format('woff2')}}")
    return "".join(out)


PAGINA = """<!doctype html><html lang="it"><head><meta charset="utf-8"><style>
__FONTS__
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0b1220}
body{font-family:'Manrope',sans-serif;color:#f0f4ff;position:relative}
canvas{position:absolute;inset:0}
.ui{position:absolute;inset:0;z-index:3}
header{position:absolute;top:74px;left:88px;display:flex;align-items:center;gap:18px}
header img{height:60px;display:block}
header span{font-family:'Space Grotesk';font-weight:700;font-size:32px;letter-spacing:-.5px}
#prezzo{position:absolute;left:0;right:0;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:300px;line-height:1;letter-spacing:-14px;
 font-variant-numeric:tabular-nums;text-shadow:0 24px 80px rgba(11,18,32,.9)}
#prezzo small{font-size:.4em;letter-spacing:-6px}
#conta{position:absolute;left:0;right:0;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:54px;letter-spacing:-1px;color:#8fa8c8;font-variant-numeric:tabular-nums}
#testo{position:absolute;left:80px;right:80px;text-align:center;
 font-family:'Space Grotesk';font-weight:700;font-size:66px;line-height:1.12;letter-spacing:-1.5px}
#testo b{display:inline-block;font-weight:700;transform-origin:50% 100%}
#slogan{position:absolute;left:70px;right:70px;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:82px;line-height:1.08;letter-spacing:-2px;opacity:0}
#slogan em{font-style:normal;color:#22c55e}
footer{position:absolute;left:88px;right:88px;bottom:80px;display:flex;justify-content:space-between;
 font-size:26px;color:#546880}
</style></head><body>
<canvas id="cv" width="1080" height="1920"></canvas>
<div class="ui">
 <header><img src="__LOGO__" alt=""><span>Accumunation</span></header>
 <div id="prezzo"></div>
 <div id="conta"></div>
 <div id="testo"></div>
 <div id="slogan">Il prezzo pieno<br>non si augura<br>a <em>nessuno</em>.</div>
 <footer><span>accumunation.it</span><span>SALVA IL POST</span></footer>
</div>
<script>
const WD=__WORDS__, DUR=__DUR__, SOGLIE=__SOGLIE__, SLOG=__SLOGAN__;
window.TOT=DUR;
const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
const P=[]; // persone: nascono in fondo e salgono al loro posto
let seed=7; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
const N=500, COL=28, RIGA=27, X0=76, PASSO=(1080-152)/(COL-1), BASE=1780;
for(let i=0;i<N;i++){
  const c=i%COL, r=Math.floor(i/COL);
  // folla organica: sfalso le righe, sparpaglio, e vario la taglia
  const off = (r%2) ? PASSO*0.5 : 0;
  P.push({x:X0+c*PASSO+off+(rnd()-.5)*17,
          y:BASE-r*RIGA+(rnd()-.5)*13,
          s:0.85+rnd()*0.5,
          sx:(rnd()-.5)*140, sy:120+rnd()*90});
}
function ease(x){return x<0?0:x>1?1:1-Math.pow(1-x,3);}
function easeIO(x){return x<0?0:x>1?1:(x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2);}
// quante persone a un dato istante
function quante(t){
  let v=0;
  for(let i=0;i<SOGLIE.length-1;i++){
    const a=SOGLIE[i], b=SOGLIE[i+1];
    if(t>=a.t && t<=b.t){ const p=easeIO((t-a.t)/(b.t-a.t)); v=a.n+(b.n-a.n)*p; }
  }
  if(t<SOGLIE[0].t) v=SOGLIE[0].n;
  if(t>SOGLIE[SOGLIE.length-1].t) v=SOGLIE[SOGLIE.length-1].n;
  return v;
}
function prezzoDa(n){ // 100 -> 62 al crescere del gruppo, a scaglioni morbidi
  const S=[[1,100],[50,85],[200,72],[500,62]];
  if(n<=1) return 100;
  for(let i=0;i<S.length-1;i++){
    if(n>=S[i][0]&&n<=S[i+1][0]){
      const p=(n-S[i][0])/(S[i+1][0]-S[i][0]);
      return S[i][1]+(S[i+1][1]-S[i][1])*p;
    }
  }
  return 62;
}
function persona(x,y,s,a){
  ctx.globalAlpha=a;
  ctx.beginPath(); ctx.arc(x,y-10.5*s,4.1*s,0,6.2832); ctx.fill();
  ctx.beginPath(); ctx.moveTo(x-6*s,y); ctx.quadraticCurveTo(x,y-11.5*s,x+6*s,y); ctx.closePath(); ctx.fill();
}
function setT(t){
  ctx.clearRect(0,0,1080,1920);
  // spinta di camera lenta e costante
  const zoom=1+0.055*(t/DUR);
  ctx.save(); ctx.translate(540,1120); ctx.scale(zoom,zoom); ctx.translate(-540,-1120);
  const n=quante(t);
  // bagliore che cresce col gruppo
  const g=ctx.createRadialGradient(540,1750,60,540,1750,1000);
  const f=Math.min(1,n/500);
  g.addColorStop(0,'rgba(34,197,94,'+(0.05+0.16*f).toFixed(3)+')');
  g.addColorStop(1,'rgba(34,197,94,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,1080,1920);
  ctx.fillStyle='#22c55e';
  
  for(let i=0;i<N;i++){
    const p=P[i];
    const q=(n-i);            // quanto e' "arrivata" questa persona
    if(q<=0) continue;
    const e=ease(Math.min(1,q/7));
    const y=p.y+(1-e)*p.sy, x=p.x+(1-e)*p.sx;
    persona(x,y,p.s*(0.7+0.3*e),Math.min(1,e*1.15)*(0.5+0.5*f));
  }
  ctx.restore();
  // velo scuro sopra la folla, per staccarla dal testo
  const vg=ctx.createLinearGradient(0,1050,0,1330);
  vg.addColorStop(0,'rgba(11,18,32,.95)'); vg.addColorStop(1,'rgba(11,18,32,0)');
  ctx.fillStyle=vg; ctx.fillRect(0,1050,1080,290);
  const vb=ctx.createLinearGradient(0,1830,0,1920);
  vb.addColorStop(0,'rgba(11,18,32,0)'); vb.addColorStop(1,'rgba(11,18,32,.95)');
  ctx.fillStyle=vb; ctx.fillRect(0,1830,1080,90);
  // prezzo: scende fisicamente mentre le persone salgono
  const pr=prezzoDa(n);
  const el=document.getElementById('prezzo');
  const alto=360, basso=720;
  el.style.top=(alto+(basso-alto)*Math.min(1,n/500)).toFixed(1)+'px';
  el.style.color = n>1.5 ? '#22c55e' : '#f0f4ff';
  el.innerHTML=Math.round(pr)+'<small> &euro;</small>';
  const c=document.getElementById('conta');
  c.style.top=(alto+(basso-alto)*Math.min(1,n/500)+310).toFixed(1)+'px';
  c.textContent = n<1.5 ? '1 persona' : Math.round(n).toLocaleString('it-IT')+' persone';
  // testo a parole, non a schermate
  const T=document.getElementById('testo');
  let html='', vis=false;
  for(let i=0;i<WD.length;i++){
    const w=WD[i];
    if(t>=w[0]-0.12 && t<=w[1]+0.55){
      vis=true;
      const inn=Math.min(1,(t-(w[0]-0.12))/0.16), out=Math.min(1,((w[1]+0.55)-t)/0.3);
      const o=Math.min(inn,out), sc=(0.86+0.14*ease(inn));
      html+='<b style="opacity:'+o.toFixed(2)+';transform:scale('+sc.toFixed(3)+')">'+w[2]+'</b> ';
    }
  }
  T.innerHTML=html;
  T.style.top='250px';
  T.style.opacity = (t>SLOG-0.2)?'0':'1';
  // slogan finale
  const S=document.getElementById('slogan');
  const so=Math.min(1,Math.max(0,(t-SLOG)/0.45));
  S.style.opacity=so.toFixed(2);
  S.style.top=(250+(1-so)*22).toFixed(0)+'px';
}
setT(0);
</script></body></html>"""


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    html = (PAGINA.replace("__FONTS__", fonts_css(spec["font_root"]))
                  .replace("__LOGO__", logo_uri(spec["logo_path"]))
                  .replace("__WORDS__", json.dumps(spec["parole"], ensure_ascii=False))
                  .replace("__DUR__", str(spec["durata"]))
                  .replace("__SOGLIE__", json.dumps(spec["soglie"]))
                  .replace("__SLOGAN__", str(spec["slogan_da"])))
    pathlib.Path(sys.argv[2]).write_text(html, encoding="utf-8")
    print(sys.argv[2])

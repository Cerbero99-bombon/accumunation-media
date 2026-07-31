#!/usr/bin/env python3
"""Reel a movimento continuo: una sola inquadratura, niente stacchi.

L'idea visiva e' il meccanismo stesso di Accumunation: le persone si accumulano dal basso e il
prezzo, appeso in alto, scende fisicamente verso di loro fino a posarcisi sopra.
Non e' una sequenza di immagini con una dissolvenza: e' una cosa sola che si muove.

Revisione 31/07/2026 (v2), dopo aver guardato i fotogrammi della v1:
- palette: era navy freddo #0b1220, cioe' l'errore gia' pagato il 28/07. Ora il carbone caldo
  del brand (#16120D) con crema e verde del sito;
- la folla aveva figure tutte uguali su griglia regolare e si leggeva come **texture**, non come
  gente. Ora ha prospettiva: le file davanti sono grandi e nitide, quelle dietro piccole e velate;
- la folla arrivava a meta' schermo e sotto restava un buco nero. Ora arriva in alto e il prezzo
  le scende addosso: niente zona morta;
- il testo entrava **una parola per volta** e sembrava un sottotitolo smarrito. Ora entra la
  frase intera, con la parola pronunciata in quel momento accesa;
- dopo il settimo secondo il video era **fermo**: la folla era gia' tutta arrivata e restava
  solo lo zoom impercettibile. Ora la folla respira, la camera accelera la spinta nella seconda
  meta' e il prezzo continua a calare di posizione fino all'ultimo fotogramma.
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
html,body{width:1080px;height:1920px;overflow:hidden;background:#16120D}
body{font-family:'Manrope',sans-serif;color:#FBF8F2;position:relative}
canvas{position:absolute;inset:0}
.ui{position:absolute;inset:0;z-index:3}
header{position:absolute;top:74px;left:88px;display:flex;align-items:center;gap:18px}
header img{height:60px;display:block}
header span{font-family:'Space Grotesk';font-weight:700;font-size:32px;letter-spacing:-.5px}
#testo{position:absolute;left:70px;right:70px;text-align:center;
 font-family:'Space Grotesk';font-weight:700;font-size:76px;line-height:1.1;letter-spacing:-2px}
#testo b{display:inline-block;font-weight:700;transform-origin:50% 100%;color:#7D7161}
#testo b.on{color:#FBF8F2}
#prezzo{position:absolute;left:0;right:0;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:320px;line-height:1;letter-spacing:-16px;
 font-variant-numeric:tabular-nums;text-shadow:0 30px 90px rgba(22,18,13,.95)}
#prezzo small{font-size:.38em;letter-spacing:-6px}
#conta{position:absolute;left:0;right:0;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:56px;letter-spacing:-1px;color:#B5A896;font-variant-numeric:tabular-nums;
 text-shadow:0 8px 40px rgba(22,18,13,.95)}
#nota{position:absolute;top:100px;right:88px;text-align:right;font-size:24px;color:#B5A896;
 letter-spacing:.5px;opacity:.8}
#slogan{position:absolute;left:70px;right:70px;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:88px;line-height:1.08;letter-spacing:-2.5px;opacity:0}
#slogan em{font-style:normal;color:#1FB877}
footer{position:absolute;left:88px;right:88px;bottom:74px;display:flex;justify-content:space-between;
 font-size:27px;color:#FBF8F2;opacity:.72;letter-spacing:.5px;
 text-shadow:0 4px 22px rgba(22,18,13,.95),0 0 8px rgba(22,18,13,.9)}
</style></head><body>
<canvas id="cv" width="1080" height="1920"></canvas>
<div class="ui">
 <header><img src="__LOGO__" alt=""><span>Accumunation</span></header>
 <div id="testo"></div>
 <div id="prezzo"></div>
 <div id="conta"></div>
 <div id="nota">esempio illustrativo</div>
 <div id="slogan">Il prezzo pieno<br>non si augura<br>a <em>nessuno</em>.</div>
 <footer><span>accumunation.it</span><span>SALVA IL POST</span></footer>
</div>
<script>
const WD=__WORDS__, DUR=__DUR__, SOGLIE=__SOGLIE__, SLOG=__SLOGAN__;
window.TOT=DUR;
const cv=document.getElementById('cv'), ctx=cv.getContext('2d');

// ---- la folla ---------------------------------------------------------------
// Prospettiva: la fila davanti e' grande e opaca, quelle dietro rimpiccioliscono e sbiadiscono.
// Senza questo si legge come una texture verde, che e' l'errore della v1.
const N=500, COL=25, FILE=Math.ceil(N/COL);
const SP0=64, K=0.928, S0=2.45, YBASE=1878;
let seed=7; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
const P=[]; let yy=YBASE;
for(let r=0;r<FILE;r++){
  const s=S0*Math.pow(K,r), sp=SP0*Math.pow(K,r);
  const off=(r%2?0.5:0)+(rnd()-.5)*0.3;
  for(let c=0;c<COL;c++){
    const i=r*COL+c; if(i>=N) break;
    P.push({r:r,
            x:-60+(c+off)*((1080+120)/(COL-1))+(rnd()-.5)*26*s,
            y:yy+(rnd()-.5)*11*s,
            s:s*(0.88+rnd()*0.26),
            a:Math.max(0.42,1-r*0.032),
            f:rnd()*6.283,
            sx:(rnd()-.5)*180, sy:150+rnd()*140});
  }
  yy-=sp;
}
// La folla si aggrega attorno alla prima persona: entra il centro della fila, poi i lati.
P.sort((a,b)=> (a.r-b.r) || (Math.abs(a.x-540)-Math.abs(b.x-540)) );
function ease(x){return x<0?0:x>1?1:1-Math.pow(1-x,3);}
function easeIO(x){return x<0?0:x>1?1:(x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2);}
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
function prezzoDa(n){ // scala canonica 100/85/72/62, dentro la banda R-025
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
  ctx.beginPath(); ctx.arc(x,y-11*s,4.2*s,0,6.2832); ctx.fill();
  ctx.beginPath(); ctx.moveTo(x-6.2*s,y); ctx.quadraticCurveTo(x,y-12*s,x+6.2*s,y);
  ctx.closePath(); ctx.fill();
}
function setT(t){
  ctx.clearRect(0,0,1080,1920);
  const n=quante(t), f=Math.min(1,n/500);
  // la camera spinge, e spinge di piu' quando la folla e' arrivata: cosi' la seconda meta'
  // del reel non e' mai ferma
  const zoom=1+0.05*(t/DUR)+0.045*f*ease(Math.max(0,(t-6)/(DUR-6)));
  ctx.save(); ctx.translate(540,1500); ctx.scale(zoom,zoom); ctx.translate(-540,-1500);
  const g=ctx.createRadialGradient(540,1820,80,540,1820,1150);
  g.addColorStop(0,'rgba(31,184,119,'+(0.05+0.20*f).toFixed(3)+')');
  g.addColorStop(1,'rgba(31,184,119,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,1080,1920);
  ctx.fillStyle='#1FB877';
  // "Una persona sola": finche' e' una sola, va vista. In fondo alla griglia sarebbe un puntino
  // in mezzo a un buco nero, che e' come si presentava la v2.
  const solo=Math.max(0,Math.min(1,(12-n)/11));
  for(let i=N-1;i>=0;i--){          // dal fondo verso la camera: chi e' davanti copre chi e' dietro
    const p=P[i], q=(n-i);
    if(q<=0) continue;
    const e=ease(Math.min(1,q/9));
    // respiro: non si nota da fermi, ma tiene viva l'immagine quando la folla e' completa
    const br=Math.sin(t*0.9+p.f)*2.6*p.s, bry=Math.sin(t*1.27+p.f)*1.4*p.s;
    let px=p.x+(1-e)*p.sx+br, py=p.y+(1-e)*p.sy+bry, ps=p.s*(0.72+0.28*e), pa=Math.min(1,e*1.15)*p.a;
    if(i===0 && solo>0){        // la prima sale al centro e si ingrandisce, poi rientra nei ranghi
      px+=(540-px)*solo; py+=(1548-py)*solo; ps+=(4.6-ps)*solo; pa=Math.max(pa,solo);
    }
    persona(px,py,ps,pa);
  }
  ctx.restore();
  // velo caldo sopra la folla: stacca il testo senza tagliarla con una riga netta
  const vg=ctx.createLinearGradient(0,1010,0,1420);
  vg.addColorStop(0,'rgba(22,18,13,.92)'); vg.addColorStop(1,'rgba(22,18,13,0)');
  ctx.fillStyle=vg; ctx.fillRect(0,1010,1080,410);
  const vb=ctx.createLinearGradient(0,1810,0,1920);
  vb.addColorStop(0,'rgba(22,18,13,0)'); vb.addColorStop(1,'rgba(22,18,13,.9)');
  ctx.fillStyle=vb; ctx.fillRect(0,1810,1080,110);

  // prezzo: scende addosso alla folla, non resta appeso in alto
  const pr=prezzoDa(n);
  const el=document.getElementById('prezzo');
  const alto=560, basso=1010;
  const top=alto+(basso-alto)*easeIO(f)+18*ease(Math.max(0,(t-7.2)/(DUR-7.2)));
  el.style.top=top.toFixed(1)+'px';
  el.style.color = n>1.5 ? '#1FB877' : '#FBF8F2';
  el.innerHTML=Math.round(pr)+'<small> &euro;</small>';
  const c=document.getElementById('conta');
  c.style.top=(top+336).toFixed(1)+'px';
  c.textContent = n<1.5 ? '1 persona' : Math.round(n).toLocaleString('it-IT')+' persone';
  document.getElementById('nota').style.opacity = t>SLOG-0.2 ? '0' : '0.8';

  // testo: entra la FRASE, con accesa la parola che si sta pronunciando
  const T=document.getElementById('testo');
  let fr=-1;
  for(let i=0;i<WD.length;i++){ if(t>=WD[i][0]-0.30 && t<=WD[i][1]+0.62) fr=WD[i][3]; }
  let html='', op=0;
  if(fr>=0){
    const g2=WD.filter(w=>w[3]===fr);
    const a0=g2[0][0]-0.30, b0=g2[g2.length-1][1]+0.62;
    op=Math.min(1,(t-a0)/0.22,(b0-t)/0.34);
    for(const w of g2){
      const on=(t>=w[0]-0.05 && t<=w[1]+0.22);
      html+='<b class="'+(on?'on':'')+'" style="transform:scale('+(on?1:0.965)+')">'+w[2]+'</b> ';
    }
  }
  T.innerHTML=html;
  T.style.top='250px';
  T.style.opacity=(t>SLOG-0.25)?'0':Math.max(0,op).toFixed(2);

  const S=document.getElementById('slogan');
  const so=Math.min(1,Math.max(0,(t-SLOG)/0.45));
  S.style.opacity=so.toFixed(2);
  S.style.top=(240+(1-so)*24).toFixed(0)+'px';
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

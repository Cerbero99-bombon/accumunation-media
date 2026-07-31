#!/usr/bin/env python3
"""Motore dello stile D: una sola inquadratura che si muove per tutta la durata.

Il motore e' lo scheletro condiviso di TUTTI i reel a movimento continuo: palette calda del
brand, testo del parlato a frasi con la parola pronunciata accesa, chiusura con slogan e
dominio, riga della fonte, zone sicure di Instagram rispettate, camera che spinge.

Quello che cambia da reel a reel e' il MOTIVO: la cosa che si muove al centro.
Ogni motivo e' un blocco JS registrato qui sotto con la stessa interfaccia:
    init()     -> costruisce il suo stato (e l'eventuale DOM dentro #mezzo)
    draw(t)    -> disegna l'istante t sul canvas e aggiorna il suo DOM

Motivi disponibili:
    folla      il meccanismo di Accumunation: le persone si accumulano, il prezzo scende
    conto      un countdown che scade e non succede niente, poi il muro dei 393

Uso:
    python3 tools/stileD/motore.py spec.json out.html
    python3 tools/stileD/shoot.py out.html <dir> <durata>

Spec (JSON):
    motivo     nome del motivo
    cfg        parametri del motivo (vedi i commenti nel JS)
    parole     words.json della voce, tal quale (il 4o campo e' l'indice di frase)
    durata     secondi del video
    slogan_da  istante in cui entra lo slogan finale (di solito l'attacco dell'ultima frase)
    fonte      riga della fonte a schermo (null se il reel non cita dati esterni)
    nota       riga piccola in alto a destra, es. "esempio illustrativo" (null per niente)
    font_root  cartella dei woff2
    logo_path  png del marchio

Regole ereditate dalle revisioni (non toglierle senza un motivo scritto):
- palette CALDA da references/brand.md: fondo #16120D, crema #FBF8F2, verde #1FB877.
  Il navy #0b1220 e' l'errore gia' pagato due volte;
- il testo entra a FRASI, mai a parole sciolte;
- niente footer in basso: la UI di Instagram copre gli ultimi ~400px. Il dominio sta
  nella chiusura, sotto lo slogan;
- il video non deve MAI stare fermo piu' di un secondo e mezzo: ogni motivo deve avere
  un "respiro" anche quando la sua azione principale e' finita.
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


# ---------------------------------------------------------------- motivi (JS)

MOTIVO_FOLLA = r"""
// FOLLA — le persone si accumulano dal basso, il prezzo scende loro addosso.
// cfg: { soglie:[{t,n}...], scala:[[n,prezzo]...] }
MOTIVO = (function(){
  const cfg = CFG;
  const N=500, COL=25, FILE=Math.ceil(N/COL);
  const SP0=64, K=0.928, S0=2.45, YBASE=1878;
  let seed=7; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
  const P=[]; let yy=YBASE;
  for(let r=0;r<FILE;r++){
    const s=S0*Math.pow(K,r), sp=SP0*Math.pow(K,r);
    const off=(r%2?0.5:0)+(rnd()-.5)*0.3;
    for(let c=0;c<COL;c++){
      const i=r*COL+c; if(i>=N) break;
      P.push({r:r, x:-60+(c+off)*((1080+120)/(COL-1))+(rnd()-.5)*26*s,
              y:yy+(rnd()-.5)*11*s, s:s*(0.88+rnd()*0.26),
              a:Math.max(0.42,1-r*0.032), f:rnd()*6.283,
              sx:(rnd()-.5)*180, sy:150+rnd()*140});
    }
    yy-=sp;
  }
  P.sort((a,b)=> (a.r-b.r) || (Math.abs(a.x-540)-Math.abs(b.x-540)) );
  function quante(t){
    const S=cfg.soglie; let v=S[0].n;
    for(let i=0;i<S.length-1;i++){
      if(t>=S[i].t && t<=S[i+1].t){ v=S[i].n+(S[i+1].n-S[i].n)*easeIO((t-S[i].t)/(S[i+1].t-S[i].t)); }
    }
    if(t>S[S.length-1].t) v=S[S.length-1].n;
    return v;
  }
  function prezzoDa(n){
    const S=cfg.scala;
    if(n<=S[0][0]) return S[0][1];
    for(let i=0;i<S.length-1;i++)
      if(n>=S[i][0]&&n<=S[i+1][0])
        return S[i][1]+(S[i+1][1]-S[i][1])*((n-S[i][0])/(S[i+1][0]-S[i][0]));
    return S[S.length-1][1];
  }
  function persona(x,y,s,a){
    ctx.globalAlpha=a;
    ctx.beginPath(); ctx.arc(x,y-11*s,4.2*s,0,6.2832); ctx.fill();
    ctx.beginPath(); ctx.moveTo(x-6.2*s,y); ctx.quadraticCurveTo(x,y-12*s,x+6.2*s,y);
    ctx.closePath(); ctx.fill();
  }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="prezzo"></div><div id="conta"></div>';
    },
    draw(t){
      const n=quante(t), f=Math.min(1,n/cfg.soglie[cfg.soglie.length-1].n);
      const zoom=1+0.05*(t/DUR)+0.045*f*ease(Math.max(0,(t-6)/(DUR-6)));
      ctx.save(); ctx.translate(540,1500); ctx.scale(zoom,zoom); ctx.translate(-540,-1500);
      const g=ctx.createRadialGradient(540,1820,80,540,1820,1150);
      g.addColorStop(0,'rgba(31,184,119,'+(0.05+0.20*f).toFixed(3)+')');
      g.addColorStop(1,'rgba(31,184,119,0)');
      ctx.fillStyle=g; ctx.fillRect(0,0,1080,1920);
      ctx.fillStyle='#1FB877';
      const solo=Math.max(0,Math.min(1,(12-n)/11));
      for(let i=N-1;i>=0;i--){
        const p=P[i], q=(n-i);
        if(q<=0) continue;
        const e=ease(Math.min(1,q/9));
        const br=Math.sin(t*0.9+p.f)*2.6*p.s, bry=Math.sin(t*1.27+p.f)*1.4*p.s;
        let px=p.x+(1-e)*p.sx+br, py=p.y+(1-e)*p.sy+bry,
            ps=p.s*(0.72+0.28*e), pa=Math.min(1,e*1.15)*p.a;
        if(i===0 && solo>0){ px+=(540-px)*solo; py+=(1548-py)*solo; ps+=(4.6-ps)*solo; pa=Math.max(pa,solo); }
        persona(px,py,ps,pa);
      }
      ctx.restore();
      velo();
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
    }
  };
})();
"""

MOTIVO_CONTO = r"""
// CONTO — un countdown scade e non succede niente; poi il muro dei countdown tutti a zero.
// cfg: { da: secondi di partenza del timer (600 = "10:00"),
//        zero_a:   istante in cui il timer tocca 00:00 (la voce dice "scade"),
//        pill_a:   istante della pillola "l'offerta e' ancora li'" ("non succede niente"),
//        muro_a:   istante in cui nasce il muro ("trecentonovantatre'"),
//        muro_n:   quanti countdown nel muro (393),
//        evid_a:   istante in cui si accendono i 22 ("ventidue aziende"),
//        evid_n:   quanti se ne accendono (22) }
MOTIVO = (function(){
  const cfg = CFG;
  let seed=11; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
  // muro: 12 colonne, righe quante servono, dentro la fascia y [640,1500]
  const MC=12, MN=cfg.muro_n, MR=Math.ceil(MN/MC);
  const MX0=84, MXW=(1080-168)/(MC-1), MY0=680, MYH=Math.min(46,(1470-MY0)/(MR-1));
  const T=[];
  for(let i=0;i<MN;i++){
    const c=i%MC, r=Math.floor(i/MC);
    T.push({x:MX0+c*MXW, y:MY0+r*MYH,
            ord:rnd(),                 // onda di comparsa
            ph:rnd()*6.283,            // fase del lampeggio dei due punti
            ev:false});
  }
  // i 22 evidenziati: sparsi ma riproducibili
  const idx=[...Array(MN).keys()];
  for(let i=MN-1;i>0;i--){ const j=Math.floor(rnd()*(i+1)); [idx[i],idx[j]]=[idx[j],idx[i]]; }
  for(let k=0;k<cfg.evid_n;k++) T[idx[k]].ev=true;
  function mmss(s){
    s=Math.max(0,s);
    const m=Math.floor(s/60), ss=Math.floor(s%60);
    return String(m).padStart(2,'0')+':'+String(ss).padStart(2,'0');
  }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="timer"></div><div id="sotto"><i></i></div><div id="grande"></div>';
      document.querySelector('#sotto i').textContent = cfg.pill || '';
    },
    draw(t){
      const zoom=1+0.05*(t/DUR)+0.03*ease(Math.max(0,(t-cfg.muro_a)/(DUR-cfg.muro_a)));
      const tm=document.getElementById('timer'), so=document.getElementById('sotto'),
            gr=document.getElementById('grande');
      // ---- fase 1: il timer grande
      const wallP=Math.min(1,Math.max(0,(t-cfg.muro_a)/0.9));
      const rest = t<cfg.zero_a ? cfg.da*(1-easeIO(t/cfg.zero_a)) : 0;
      const blink = (Math.floor(t*2)%2===0);
      const shake = (t>cfg.zero_a && t<cfg.zero_a+0.5) ? Math.sin((t-cfg.zero_a)*60)*9*(1-(t-cfg.zero_a)/0.5) : 0;
      const tsc = 1-0.62*wallP;               // il timer si ritira quando nasce il muro
      // dopo lo zero il timer "muore": affonda piano, con la pillola dietro.
      // Serve anche a non stare mai fermi: il silenzio e' il contenuto, non l'immobilita'.
      const sink = t>cfg.zero_a ? Math.min(1,(t-cfg.zero_a)/(cfg.muro_a-cfg.zero_a))*36 : 0;
      tm.style.transform='translateX('+shake.toFixed(1)+'px) scale('+tsc.toFixed(3)+')';
      tm.style.opacity=(1-wallP).toFixed(2);
      tm.style.top=(660-180*wallP+Math.sin(t*1.7)*5+sink).toFixed(1)+'px';
      tm.innerHTML=mmss(rest).replace(':', blink||t>cfg.zero_a ? ':' : '<span style="opacity:.25">:</span>');
      tm.style.color = t<cfg.zero_a ? '#FBF8F2' : '#7D7161';
      // pillola "l'offerta e' ancora li'"
      const po=Math.min(1,Math.max(0,(t-cfg.pill_a)/0.35))*(1-wallP);
      so.style.opacity=po.toFixed(2);
      so.style.top=(1090+(1-po)*18+sink).toFixed(1)+'px';
      so.style.transform='scale('+(1+0.04*Math.sin(t*3.4)).toFixed(3)+')';
      // ---- fase 2: il muro
      if(wallP>0){
        ctx.save(); ctx.translate(540,1050); ctx.scale(zoom,zoom); ctx.translate(-540,-1050);
        ctx.textAlign='center'; ctx.textBaseline='middle';
        const evP=Math.min(1,Math.max(0,(t-cfg.evid_a)/0.6));
        for(const c of T){
          const arriva=Math.min(1,Math.max(0,(wallP*1.35-c.ord)/0.35));
          if(arriva<=0) continue;
          const blinkc=(Math.sin(t*3.1+c.ph)+1)/2;
          let col='#7D7161', al=0.34+0.30*arriva*(0.6+0.4*blinkc);
          if(c.ev && evP>0){ col='#1FB877'; al=0.25+0.75*evP*(0.75+0.25*Math.sin(t*4+c.ph)); }
          else if(evP>0){ al*=(1-0.55*evP); }
          // allo slogan il muro si spegne ma continua a RESPIRARE: e' il moto che tiene
          // vivo il finale (il collaudo boccia ogni finestra ferma oltre 1.5s)
          if(t>SLOG){
            const giu=Math.min(1,(t-SLOG)*1.8);
            al = c.ev ? (al*(1-giu) + giu*(0.10+0.30*((Math.sin(t*4+c.ph)+1)/2)))
                      : (al*(1-giu) + giu*(0.05+0.16*blinkc));
          }
          ctx.globalAlpha=Math.max(0, Math.min(1, al));
          ctx.fillStyle=col;
          ctx.font='700 '+(24+3*(c.ev&&evP>0?1:0))+'px "Space Grotesk"';
          ctx.fillText('00:00', c.x, c.y+(1-arriva)*26);
        }
        ctx.restore();
        // numero grande sopra il muro: 393, poi 22
        const evP2=Math.min(1,Math.max(0,(t-cfg.evid_a)/0.45));
        const num = evP2>0.5 ? String(cfg.evid_n) : String(cfg.muro_n);
        const flip = evP2>0.5 ? Math.min(1,(evP2-0.5)*4) : 1;
        gr.style.opacity=(wallP*(t>SLOG?Math.max(0,1-(t-SLOG)*2.2):1)).toFixed(2);
        gr.style.transform='scale('+(0.94+0.06*flip)+')';
        gr.textContent=num;
        gr.style.color = evP2>0.5 ? '#1FB877' : '#FBF8F2';
      } else gr.style.opacity=0;
    }
  };
})();
"""

MOTIVI = {"folla": MOTIVO_FOLLA, "conto": MOTIVO_CONTO}

# ---------------------------------------------------------------- pagina

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
#nota{position:absolute;top:104px;right:88px;font-size:24px;color:#B5A896;opacity:.8}
#testo{position:absolute;top:250px;left:90px;right:90px;text-align:center;
 font-family:'Space Grotesk';font-weight:700;line-height:1.12;letter-spacing:-2px}
#testo b{display:inline-block;font-weight:700;color:#7D7161}
#testo b.on{color:#FBF8F2}
#mezzo{position:absolute;inset:0}
#prezzo{position:absolute;left:0;right:0;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:320px;line-height:1;letter-spacing:-16px;
 font-variant-numeric:tabular-nums;text-shadow:0 30px 90px rgba(22,18,13,.95)}
#prezzo small{font-size:.38em;letter-spacing:-6px}
#conta{position:absolute;left:0;right:0;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:56px;letter-spacing:-1px;color:#B5A896;font-variant-numeric:tabular-nums;
 text-shadow:0 8px 40px rgba(22,18,13,.95)}
#timer{position:absolute;left:0;right:0;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:290px;line-height:1;letter-spacing:-8px;font-variant-numeric:tabular-nums;
 text-shadow:0 30px 90px rgba(22,18,13,.95)}
#sotto{position:absolute;left:0;right:0;text-align:center}
#sotto i{display:inline-block;font-style:normal;font-weight:800;font-size:40px;letter-spacing:1px;
 color:#0A2418;background:#1FB877;border-radius:999px;padding:22px 44px}
#grande{position:absolute;top:920px;left:0;right:0;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:230px;line-height:1;letter-spacing:-10px;
 text-shadow:0 26px 80px rgba(22,18,13,.98),0 0 60px rgba(22,18,13,.9);opacity:0}
#fonte{position:absolute;left:90px;right:90px;top:1506px;text-align:center;font-size:26px;
 color:#B5A896;opacity:0;letter-spacing:.3px}
#slogan{position:absolute;left:70px;right:70px;top:240px;text-align:center;font-family:'Space Grotesk';
 font-weight:700;font-size:88px;line-height:1.08;letter-spacing:-2.5px;opacity:0}
#slogan em{font-style:normal;color:#1FB877}
#dominio{position:absolute;left:0;right:0;top:640px;text-align:center;font-weight:600;
 font-size:36px;color:#B5A896;opacity:0;letter-spacing:.5px}
</style></head><body>
<canvas id="cv" width="1080" height="1920"></canvas>
<div class="ui">
 <header><img src="__LOGO__" alt=""><span>Accumunation</span></header>
 __NOTA__
 <div id="testo"></div>
 <div id="mezzo"></div>
 __FONTE__
 <div id="slogan">Il prezzo pieno<br>non si augura<br>a <em>nessuno</em>.</div>
 <div id="dominio">accumunation.it</div>
</div>
<script>
const WD=__WORDS__, DUR=__DUR__, SLOG=__SLOGAN__, CFG=__CFG__;
window.TOT=DUR;
const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
function ease(x){return x<0?0:x>1?1:1-Math.pow(1-x,3);}
function easeIO(x){return x<0?0:x>1?1:(x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2);}
// velo caldo sopra e sotto la fascia centrale: stacca il disegno dal testo
function velo(){
  const vg=ctx.createLinearGradient(0,1010,0,1420);
  vg.addColorStop(0,'rgba(22,18,13,.92)'); vg.addColorStop(1,'rgba(22,18,13,0)');
  ctx.fillStyle=vg; ctx.fillRect(0,1010,1080,410);
  const vb=ctx.createLinearGradient(0,1810,0,1920);
  vb.addColorStop(0,'rgba(22,18,13,0)'); vb.addColorStop(1,'rgba(22,18,13,.9)');
  ctx.fillStyle=vb; ctx.fillRect(0,1810,1080,110);
}
let MOTIVO=null;
__MOTIVO__
MOTIVO.init();
function setT(t){
  ctx.clearRect(0,0,1080,1920);
  MOTIVO.draw(t);
  // ---- testo del parlato, a frasi, parola corrente accesa
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
    T.style.fontSize=(g2.length>6?64:76)+'px';
  }
  T.innerHTML=html;
  T.style.opacity=(t>SLOG-0.25)?'0':Math.max(0,op).toFixed(2);
  // ---- fonte
  const F=document.getElementById('fonte');
  if(F){ F.style.opacity = (t>__FONTE_DA__ && t<SLOG-0.2) ? '0.85' : '0'; }
  // ---- chiusura: slogan + dominio
  const S=document.getElementById('slogan');
  const so=Math.min(1,Math.max(0,(t-SLOG)/0.45));
  S.style.opacity=so.toFixed(2);
  S.style.top=(240+(1-so)*24).toFixed(0)+'px';
  const D=document.getElementById('dominio');
  const dm=Math.min(1,Math.max(0,(t-SLOG-0.5)/0.4));
  D.style.opacity=(dm*0.9).toFixed(2);
  D.style.top=(640+(1-dm)*14).toFixed(0)+'px';
}
setT(0);
</script></body></html>"""


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    motivo = spec["motivo"]
    if motivo not in MOTIVI:
        sys.exit(f"motivo sconosciuto: {motivo} (disponibili: {', '.join(MOTIVI)})")
    nota = spec.get("nota")
    fonte = spec.get("fonte")
    html = (PAGINA.replace("__FONTS__", fonts_css(spec["font_root"]))
                  .replace("__LOGO__", logo_uri(spec["logo_path"]))
                  .replace("__NOTA__", f'<div id="nota">{nota}</div>' if nota else "")
                  .replace("__FONTE__", f'<div id="fonte">{fonte}</div>' if fonte else "")
                  .replace("__FONTE_DA__", str(spec.get("fonte_da", 0)))
                  .replace("__WORDS__", json.dumps(spec["parole"], ensure_ascii=False))
                  .replace("__DUR__", str(spec["durata"]))
                  .replace("__SLOGAN__", str(spec["slogan_da"]))
                  .replace("__CFG__", json.dumps(spec.get("cfg", {}), ensure_ascii=False))
                  .replace("__MOTIVO__", MOTIVI[motivo]))
    pathlib.Path(sys.argv[2]).write_text(html, encoding="utf-8")
    print(sys.argv[2])

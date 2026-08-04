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
        // regola del conteggio: sotto le 30 unita' l'occhio conta, quindi una figura
        // "contata" dal numero deve essere GIA' visibile: ingresso rapido (q/2).
        const e=ease(Math.min(1,q/(n<30?2:9)));
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

MOTIVO_PILA = r"""
// PILA — i capi piovono dall'alto: 4 su 5 si accatastano a sinistra (venduti), il quinto
// devia a destra, nella zona della distruzione, e si sbriciola. Finche' la legge non cala.
// cfg: { distru_a: da quando i capi a destra si sbriciolano ("finisce distrutta"),
//        vieta_a:  quando cala il sigillo VIETATO ("dal 19 luglio e' vietato"),
//        data:     testo del sigillo, es. "VIETATO|dal 19.07.2026" (| = a capo) }
MOTIVO = (function(){
  const cfg = CFG;
  let seed=23; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
  const RATE=0.44, CADUTA=0.9;
  const C=[]; let kv=0, ki=0;
  for(let i=0;i<40;i++){
    const inv = (i%5===4);
    let tx,ty;
    if(inv){ tx=772+(ki%2)*112+(rnd()-.5)*12; ty=1408-Math.floor(ki/2)*96+(rnd()-.5)*8; ki++; }
    else   { tx=168+(kv%5)*112+(rnd()-.5)*16; ty=1420-Math.floor(kv/5)*98+(rnd()-.5)*8; kv++; }
    // i primi tre partono subito (uno e' gia' a mezz'aria al fotogramma 1): il gancio
    // sta nei primi due fotogrammi, non al primo atterraggio
    const t0 = i===0 ? -0.5 : (i===1 ? -0.15 : (i===2 ? 0.12 : 0.3+i*RATE));
    C.push({t0:t0, inv:inv, tx:tx, ty:ty,
            x0:430+rnd()*220, rot:(rnd()-.5)*0.5, s:0.92+rnd()*0.2, ph:rnd()*6.283});
  }
  function capo(x,y,s,rot,col,al){
    ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s);
    ctx.globalAlpha=al; ctx.fillStyle=col;
    ctx.beginPath();                          // corpo
    ctx.moveTo(-34,-38); ctx.lineTo(34,-38); ctx.lineTo(34,42); ctx.lineTo(-34,42);
    ctx.closePath(); ctx.fill();
    ctx.beginPath();                          // maniche
    ctx.moveTo(-34,-38); ctx.lineTo(-56,-26); ctx.lineTo(-48,-4); ctx.lineTo(-34,-12);
    ctx.closePath(); ctx.fill();
    ctx.beginPath();
    ctx.moveTo(34,-38); ctx.lineTo(56,-26); ctx.lineTo(48,-4); ctx.lineTo(34,-12);
    ctx.closePath(); ctx.fill();
    ctx.globalAlpha=al*0.55; ctx.fillStyle='#16120D';   // scollo
    ctx.beginPath(); ctx.arc(0,-38,11,0,3.1416); ctx.fill();
    ctx.restore();
  }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="sigillo" style="position:absolute;left:700px;width:330px;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:44px;line-height:1.15;'+
        'letter-spacing:0;color:#0A2418;background:#1FB877;border-radius:26px;'+
        'padding:26px 10px;opacity:0"></div>';
      const s=document.getElementById('sigillo');
      s.innerHTML=(cfg.data||'VIETATO').split('|').join('<br>');
    },
    draw(t){
      const zoom=1+0.05*(t/DUR);
      ctx.save(); ctx.translate(540,1200); ctx.scale(zoom,zoom); ctx.translate(-540,-1200);
      // zona della distruzione: tratteggio a destra, finche' il divieto non la spegne
      const spenta=Math.min(1,Math.max(0,(t-cfg.vieta_a)/0.5));
      ctx.globalAlpha=0.5*(1-spenta*0.75);
      ctx.strokeStyle='#7D7161'; ctx.lineWidth=3; ctx.setLineDash([14,12]);
      ctx.strokeRect(742,880,300,600); ctx.setLineDash([]);
      if(spenta<0.5){                            // la X della distruzione
        ctx.globalAlpha=0.6*(1-spenta*2);
        ctx.lineWidth=10;
        ctx.beginPath(); ctx.moveTo(846,928); ctx.lineTo(938,1020); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(938,928); ctx.lineTo(846,1020); ctx.stroke();
      }
      for(const c of C){
        if(t<c.t0) continue;
        const p=Math.min(1,(t-c.t0)/CADUTA), e=1-Math.pow(1-p,2.4);
        let x=c.x0+(c.tx-c.x0)*e, y=-90+(c.ty+90)*e, al, col;
        const br=Math.sin(t*0.8+c.ph)*2;
        if(c.inv){
          col='#FBF8F2'; al=0.95;
          const posa=c.t0+CADUTA;
          if(t>cfg.distru_a && posa+0.7<cfg.vieta_a && t>posa+0.7){
            const d=Math.min(1,(t-posa-0.7)/0.6);   // si sbriciola, ma i brandelli RESTANO:
            al=0.95*(1-d); y+=d*46;                 // il rapporto 1-su-5 deve reggere il conteggio
            ctx.fillStyle='#B5A896';
            for(let k=0;k<7;k++){ ctx.globalAlpha=Math.min(0.75,d*1.2)*0.75;
              ctx.fillRect(c.tx-44+k*14+((k*37)%11), 1452-((k*13)%3)*8, 12, 10); }
            if(d>=1) continue;
          }
        } else { col='#7D7161'; al=0.78; }
        capo(x,y+br,c.s*(0.9+0.1*e),c.rot*(1-e*0.6),col,al);
      }
      ctx.restore();
      velo();
      // il sigillo cala con peso
      const s=document.getElementById('sigillo');
      const vp=Math.min(1,Math.max(0,(t-cfg.vieta_a)/0.45)), reb=vp<1?0:Math.sin((t-cfg.vieta_a-0.45)*9)*6*Math.exp(-(t-cfg.vieta_a-0.45)*3);
      s.style.opacity=vp.toFixed(2);
      s.style.top=(700+(1-ease(vp))* -160+reb).toFixed(1)+'px';
    }
  };
})();
"""

MOTIVO_CONTATORE = r"""
// CONTATORE — il conto in dieci secondi: un numero enorme che sale, una barra che lo
// rende fisico, una quota che si accende quando la voce la nomina.
// cfg: { fino:130, unita:"kg", conta_da:0.05, conta_a:2.1,
//        evid:{val:10, a:6.9, testo:"nei negozi"} }
MOTIVO = (function(){
  const cfg = CFG;
  let seed=31; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
  const B=[];                                     // briciole che cadono
  for(let i=0;i<160;i++) B.push({x:120+rnd()*840, t0:rnd()*DUR, v:130+rnd()*110,
                                 s:5+rnd()*9, ph:rnd()*6.283, verde:rnd()<0.12});
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="big" style="position:absolute;top:560px;left:0;right:0;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:330px;line-height:1;'+
        'letter-spacing:-14px;font-variant-numeric:tabular-nums;color:#FBF8F2;'+
        'text-shadow:0 30px 90px rgba(22,18,13,.95)"></div>'+
        '<div id="uni" style="position:absolute;top:920px;left:0;right:0;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:64px;color:#B5A896"></div>'+
        '<div id="etich" style="position:absolute;top:1252px;left:0;right:0;text-align:center;'+
        'font-weight:800;font-size:34px;color:#1FB877;opacity:0;letter-spacing:.5px"></div>';
      document.getElementById('uni').textContent=cfg.unita;
      document.getElementById('etich').textContent=cfg.evid.val+' '+cfg.unita;
      const et=document.getElementById('etich');
      et.style.textAlign='right'; et.style.right='130px'; et.style.left='auto';
    },
    draw(t){
      const zoom=1+0.05*(t/DUR);
      const p=easeIO(Math.min(1,Math.max(0,(t-cfg.conta_da)/(cfg.conta_a-cfg.conta_da))));
      const val=Math.round(cfg.fino*p);
      ctx.save(); ctx.translate(540,1100); ctx.scale(zoom,zoom); ctx.translate(-540,-1100);
      // briciole: cadono per tutta la durata, e' il flusso dello spreco
      for(const b of B){
        const life=(t-b.t0+DUR)%DUR, y=180+life*b.v;
        if(y>1860) continue;
        const al=Math.min(1,life*2)*Math.min(1,(1860-y)/160)*0.5;
        ctx.globalAlpha=Math.max(0,al);
        ctx.fillStyle=b.verde?'#1FB877':'#B5A896';
        ctx.fillRect(b.x+Math.sin(t*1.3+b.ph)*8, y, b.s, b.s);
      }
      // la barra: tutto il numero, poi la quota accesa
      const bx=120, bw=840, by=1150, bh=64;
      ctx.globalAlpha=1; ctx.fillStyle='rgba(251,248,242,.13)';
      ctx.fillRect(bx,by,bw,bh);
      ctx.fillStyle='#B5A896'; ctx.globalAlpha=0.55;
      ctx.fillRect(bx,by,bw*p,bh);
      const ev=Math.min(1,Math.max(0,(t-cfg.evid.a)/0.5));
      if(ev>0){                                   // la quota, dal fondo destro della barra
        const qw=bw*(cfg.evid.val/cfg.fino)*ev;
        ctx.globalAlpha=0.85+0.15*Math.sin(t*4);
        ctx.fillStyle='#1FB877';
        ctx.fillRect(bx+bw-qw,by,qw,bh);
      }
      ctx.restore();
      velo();
      const big=document.getElementById('big');
      big.textContent = cfg.dec ? (cfg.fino*p).toFixed(cfg.dec).replace('.',',') : val;
      big.style.transform='scale('+(1+0.02*Math.sin(t*2.1)+0.06*(1-p)).toFixed(3)+')';
      document.getElementById('etich').style.opacity=(ev*(t>SLOG?Math.max(0,1-(t-SLOG)*2):1)).toFixed(2);
      document.getElementById('big').style.opacity=document.getElementById('uni').style.opacity=
        (t>SLOG?Math.max(0,1-(t-SLOG)*2.2):1).toFixed(2);
    }
  };
})();
"""

MOTIVO_GRAFICO = r"""
// GRAFICO — la linea del prezzo negli ultimi 30 giorni: piatta, gonfiata prima dei saldi,
// crollata col cartello. La legge traccia la riga sul minimo e lo sconto vero si vede.
// cfg: { min:40, max:80, disegna_a:5.0, legge_a:8.2, falso_a:12.0,
//        badge:"−50%", vero:"0%", et_min:"minimo 30 giorni" }
MOTIVO = (function(){
  const cfg = CFG;
  const X0=110, X1=970, Y0=1400, Y1=760;          // area del grafico
  function px(g){ return X0+(X1-X0)*(g/30); }
  function py(v){ return Y0-(Y0-Y1)*((v-0)/(cfg.max*1.15)); }
  // il percorso del prezzo: piatto sul minimo, gonfiato al giorno 22, crollo al 27
  const PTS=[[0,cfg.min],[19,cfg.min],[21,cfg.max],[27,cfg.max],[27.6,cfg.min],[30,cfg.min]];
  function lungo(){ let L=0; for(let i=1;i<PTS.length;i++){
      L+=Math.hypot(px(PTS[i][0])-px(PTS[i-1][0]), py(PTS[i][1])-py(PTS[i-1][1])); } return L; }
  const LTOT=lungo();
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="badge" style="position:absolute;top:560px;left:0;right:0;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:210px;line-height:1;'+
        'letter-spacing:-8px;color:#FBF8F2;text-shadow:0 26px 80px rgba(22,18,13,.95)"></div>'+
        '<div id="vero" style="position:absolute;top:560px;left:0;right:0;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:210px;line-height:1;'+
        'letter-spacing:-8px;color:#1FB877;opacity:0;text-shadow:0 26px 80px rgba(22,18,13,.95)"></div>';
      document.getElementById('badge').textContent=cfg.badge;
      document.getElementById('vero').textContent=cfg.vero;
    },
    draw(t){
      // dopo lo slogan la camera respira (zoom che oscilla + rollio minimo): il grafico
      // resta in scena senza congelare il finale
      const fin=Math.min(1,Math.max(0,(t-SLOG)/0.8));
      const zoom=1+0.05*(t/DUR)+0.022*Math.sin(t*1.3)*fin;
      ctx.save(); ctx.translate(540,1080); ctx.scale(zoom,zoom);
      ctx.rotate(0.007*Math.sin(t*1.05)*fin); ctx.translate(-540,-1080);
      const dis=ease(Math.min(1,Math.max(0,(t-cfg.disegna_a)/2.6)));
      const leg=ease(Math.min(1,Math.max(0,(t-cfg.legge_a)/0.9)));
      const fal=ease(Math.min(1,Math.max(0,(t-cfg.falso_a)/0.7)));
      if(dis>0){
        ctx.globalAlpha=0.5; ctx.strokeStyle='#7D7161'; ctx.lineWidth=3;   // asse
        ctx.beginPath(); ctx.moveTo(X0,Y0+40); ctx.lineTo(X1,Y0+40); ctx.stroke();
        ctx.globalAlpha=0.8; ctx.fillStyle='#7D7161';
        ctx.font='600 26px Manrope'; ctx.textAlign='left';
        ctx.fillText('30 giorni fa', X0, Y0+86);
        ctx.textAlign='right'; ctx.fillText('oggi', X1, Y0+86);
        // la linea del prezzo, disegnata progressivamente
        let resta=LTOT*dis;
        ctx.lineWidth=9; ctx.lineJoin='round'; ctx.lineCap='round';
        for(let i=1;i<PTS.length && resta>0;i++){
          const ax=px(PTS[i-1][0]), ay=py(PTS[i-1][1]), bx=px(PTS[i][0]), by=py(PTS[i][1]);
          const L=Math.hypot(bx-ax,by-ay), q=Math.min(1,resta/L);
          // il tratto gonfiato si spegne quando la voce dice "non quello gonfiato"
          const gonfio = PTS[i-1][1]>cfg.min || PTS[i][1]>cfg.min;
          ctx.globalAlpha = gonfio ? 0.95-0.62*fal : 0.95;
          ctx.strokeStyle = gonfio ? (fal>0.5?'#7D7161':'#FBF8F2') : '#FBF8F2';
          ctx.beginPath(); ctx.moveTo(ax,ay); ctx.lineTo(ax+(bx-ax)*q, ay+(by-ay)*q); ctx.stroke();
          resta-=L;
        }
        // etichette prezzo
        ctx.globalAlpha=0.9*dis; ctx.fillStyle='#B5A896'; ctx.textAlign='left';
        ctx.font='700 30px "Space Grotesk"';
        ctx.fillText(cfg.min+' €', X0, py(cfg.min)-18);
        if(dis>0.75){ ctx.globalAlpha=(0.9-0.6*fal); ctx.fillText(cfg.max+' €', px(21.4), py(cfg.max)-18); }
      }
      if(leg>0){                                   // la riga della legge, sul minimo
        ctx.globalAlpha=0.95; ctx.strokeStyle='#1FB877'; ctx.lineWidth=5;
        ctx.setLineDash([18,13]); ctx.lineDashOffset=-t*24;   // scorre: vive
        ctx.beginPath(); ctx.moveTo(X0, py(cfg.min)+26); ctx.lineTo(X0+(X1-X0)*leg, py(cfg.min)+26);
        ctx.stroke(); ctx.setLineDash([]);
        ctx.globalAlpha=leg; ctx.fillStyle='#1FB877'; ctx.textAlign='right';
        ctx.font='800 28px Manrope';
        ctx.fillText(cfg.et_min, X1, py(cfg.min)+66);
      }
      ctx.restore();
      velo();
      const bd=document.getElementById('badge'), vr=document.getElementById('vero');
      const shake=(t>cfg.trema_a && t<cfg.trema_a+0.7)?Math.sin(t*50)*8:0;   // trema su "rispetto a cosa?"
      const pop=1+0.25*Math.max(0,1-t/0.4);                                  // ingresso col botto
      const galla=Math.sin(t*1.15)*9;                                        // galleggia: mai fermo
      bd.style.transform='translate('+shake.toFixed(1)+'px,'+galla.toFixed(1)+'px) scale('+
        (pop*(1+0.02*Math.sin(t*1.9))).toFixed(3)+')';
      // quando la verita' arriva, il -50% si sbarra e arretra, lo 0% verde prende il centro
      bd.style.opacity=(t>SLOG?Math.max(0,1-(t-SLOG)*2):(1-0.75*fal)).toFixed(2);
      bd.style.textDecoration = fal>0.4 ? 'line-through' : 'none';
      bd.style.left = (-(fal)*300)+'px'; bd.style.right = (fal*300)+'px';
      bd.style.fontSize = (210-90*fal)+'px'; bd.style.top=(560+30*fal)+'px';
      vr.style.opacity=(fal*(t>SLOG?Math.max(0,1-(t-SLOG)*2):1)).toFixed(2);
      vr.style.left=(fal*260)+'px'; vr.style.right=(-(fal)*260)+'px';
      vr.style.transform='scale('+(0.8+0.2*fal+0.02*Math.sin(t*2.3)).toFixed(3)+')';
    }
  };
})();
"""


MOTIVO_CARTELLINO = r"""
// CARTELLINO — un cartellino prezzo appeso che oscilla. Lo sconto e' vistoso, il prezzo
// barrato e' li'... poi la faccia si strappa e dietro c'e' la verita': MAI ESISTITO.
// cfg: { sconto:"-70%", prezzo:"299 €", strappo_a, multa_a, multa:"Antitrust · 300.000 € di sanzione" }
MOTIVO = (function(){
  const cfg = CFG;
  const CX=540, CY=1060, TW=560, TH=680;      // centro e misure del cartellino
  function tag(ctx,fill){
    ctx.beginPath();
    const r=36, x=-TW/2, y=-TH/2;
    ctx.moveTo(x+r,y); ctx.arcTo(x+TW,y,x+TW,y+TH,r); ctx.arcTo(x+TW,y+TH,x,y+TH,r);
    ctx.arcTo(x,y+TH,x,y,r); ctx.arcTo(x,y,x+TW,y,r); ctx.closePath();
    ctx.fillStyle=fill; ctx.fill();
    ctx.strokeStyle='rgba(251,248,242,.18)'; ctx.lineWidth=3; ctx.stroke();
    ctx.beginPath(); ctx.arc(0,y+64,26,0,6.2832);    // l'occhiello
    ctx.fillStyle='#16120D'; ctx.fill();
    ctx.strokeStyle='rgba(251,248,242,.3)'; ctx.stroke();
  }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="multa" style="position:absolute;left:210px;right:210px;top:1262px;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:44px;line-height:1.2;color:#0A2418;'+
        'background:#1FB877;border-radius:26px;padding:24px 16px;opacity:0"></div>';
      document.getElementById('multa').textContent=cfg.multa;
    },
    draw(t){
      const fin=Math.min(1,Math.max(0,(t-SLOG)/0.8));
      const zoom=1+0.05*(t/DUR)+0.02*Math.sin(t*1.2)*fin;
      ctx.save(); ctx.translate(540,1060); ctx.scale(zoom,zoom); ctx.translate(-540,-1060);
      // il filo
      const sw=Math.sin(t*1.35)*0.10*Math.exp(-t*0.05);          // il pendolo, non si ferma mai
      // REGOLA (errore trovato da Enrico il 02/08): filo e cartellino sono UN corpo rigido.
      // Il filo si disegna DENTRO la stessa rotazione, mai ricalcolato a parte: la versione
      // precedente usava +sin per il filo mentre il canvas ruota a -sin, e oscillavano opposti.
      ctx.save(); ctx.translate(540,150); ctx.rotate(sw); ctx.translate(-540,-150);
      ctx.strokeStyle='#7D7161'; ctx.lineWidth=4;
      ctx.beginPath(); ctx.moveTo(540,150); ctx.lineTo(540, CY-TH/2+64); ctx.stroke();
      ctx.translate(CX,CY);
      const str=ease(Math.min(1,Math.max(0,(t-cfg.strappo_a)/0.8)));
      // il retro: appare da sotto lo strappo
      if(str>0){
        tag(ctx,'#221B14');
        ctx.save(); ctx.rotate(-0.10);
        ctx.font='700 76px "Space Grotesk"'; ctx.textAlign='center';
        ctx.globalAlpha=Math.min(1,str*1.6);
        ctx.strokeStyle='#FBF8F2'; ctx.lineWidth=4;
        ctx.strokeRect(-212,-122,424,214);
        ctx.fillStyle='#FBF8F2';
        const TB=(cfg.timbro||'MAI|ESISTITO').split('|');
        if(TB.length>1){ ctx.fillText(TB[0],0,-36); ctx.fillText(TB[1],0,56); }
        else ctx.fillText(TB[0],0,10);
        ctx.restore();
      }
      // la faccia davanti: prezzo barrato e sconto urlato; si strappa e cade
      if(str<1){
        ctx.save();
        ctx.translate(str*140, str*760);                 // cade
        ctx.rotate(str*0.9);                              // ruotando
        ctx.globalAlpha=Math.pow(1-str,1.8);       // svanisce prima di toccare la riga della fonte
        tag(ctx,'#221B14');
        ctx.textAlign='center';
        ctx.fillStyle='#1FB877'; ctx.font='700 150px "Space Grotesk"';
        ctx.fillText(cfg.sconto,0,-64);
        ctx.fillStyle='#B5A896'; ctx.font='700 96px "Space Grotesk"';
        ctx.fillText(cfg.prezzo,0,110);
        const w=ctx.measureText(cfg.prezzo).width;
        ctx.strokeStyle='#B5A896'; ctx.lineWidth=8;
        ctx.beginPath(); ctx.moveTo(-w/2-16,80); ctx.lineTo(w/2+16,96); ctx.stroke();
        ctx.fillStyle='#7D7161'; ctx.font='600 34px Manrope';
        ctx.fillText(cfg.etichetta||'OUTLET',0,224);
        ctx.restore();
      }
      ctx.restore(); ctx.restore();
      velo();
      const m=document.getElementById('multa');
      const mp=Math.min(1,Math.max(0,(t-cfg.multa_a)/0.45));
      m.style.opacity=(mp*(t>SLOG+0.6?Math.max(0.55,1-(t-SLOG-0.6)):1)).toFixed(2);
      m.style.transform='scale('+(0.85+0.15*ease(mp)+0.012*Math.sin(t*2.2)).toFixed(3)+')';
    }
  };
})();
"""

MOTIVO_CONFRONTO = r"""
// CONFRONTO — due colonne, una scelta. A sinistra i pacchi cadono e finiscono in brandelli,
// e costa poco; a destra il pacco resta li', intatto, e costa di piu'. La scelta la fa il prezzo.
// cfg: { sx:{titolo:'DISTRUGGERLO', prezzo:'0,85 €'}, dx:{titolo:'DONARLO', prezzo:'di piuù'},
//        conta_a: quando appare la riga dei 20 milioni, conta:'20 milioni l'anno' }
MOTIVO = (function(){
  const cfg = CFG;
  let seed=41; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
  const DROP=[];                        // pacchi che cadono a sinistra, uno ogni 1.1s
  for(let i=0;i<17;i++) DROP.push({t0:0.3+i*1.1, x:270+(rnd()-.5)*130, rot:(rnd()-.5)*0.7});
  function pacco(x,y,s,rot,al,fill,nastro){
    ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s); ctx.globalAlpha=al;
    ctx.fillStyle=fill||'#B5A896'; ctx.fillRect(-70,-52,140,104);
    ctx.fillStyle=nastro||'#7D7161'; ctx.fillRect(-70,-10,140,20);       // il nastro
    ctx.strokeStyle='rgba(22,18,13,.35)'; ctx.lineWidth=3; ctx.strokeRect(-70,-52,140,104);
    ctx.restore();
  }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="tsx" class="col" style="left:60px"></div><div id="tdx" class="col" style="right:60px"></div>'+
        '<div id="psx" class="pr" style="left:60px"></div><div id="pdx" class="pr" style="right:60px"></div>'+
        '<div id="conta20" style="position:absolute;top:1462px;left:60px;width:440px;text-align:center;'+
        'font-weight:800;font-size:38px;color:#FBF8F2;opacity:0"></div>'+
        '<style>.col{position:absolute;top:640px;width:440px;text-align:center;'+
        'font-family:Manrope;font-weight:800;font-size:44px;letter-spacing:2px;color:#B5A896}'+
        '.pr{position:absolute;top:1330px;width:440px;text-align:center;'+
        "font-family:'Space Grotesk';font-weight:700;font-size:110px;letter-spacing:-4px;color:#FBF8F2}</style>";
      document.getElementById('tsx').textContent=cfg.sx.titolo;
      document.getElementById('tdx').textContent=cfg.dx.titolo;
      document.getElementById('psx').innerHTML=cfg.sx.prezzo;
      document.getElementById('pdx').innerHTML=cfg.dx.prezzo;
      document.getElementById('conta20').textContent=cfg.conta;
    },
    draw(t){
      const fin=Math.min(1,Math.max(0,(t-SLOG)/0.8));
      const zoom=1+0.05*(t/DUR)+0.02*Math.sin(t*1.25)*fin;
      ctx.save(); ctx.translate(540,1150); ctx.scale(zoom,zoom); ctx.translate(-540,-1150);
      ctx.strokeStyle='rgba(251,248,242,'+(t>SLOG?'.04':'.14')+')'; ctx.lineWidth=3;   // il confine
      ctx.beginPath(); ctx.moveTo(540,660); ctx.lineTo(540,1520); ctx.stroke();
      // sinistra: i pacchi cadono e si sfasciano; i brandelli restano
      let rotti=0;
      for(const d of DROP){
        if(t<d.t0) continue;
        const p=Math.min(1,(t-d.t0)/0.65), e=p*p;
        if(p<1){ pacco(d.x, 690+e*540, 1.25, d.rot*p*2, 1); }
        else rotti++;
      }
      for(let k=0;k<Math.min(rotti*7,84);k++){                     // il mucchio di brandelli
        ctx.globalAlpha=0.85; ctx.fillStyle='#B5A896';
        ctx.fillRect(105+((k*67)%340), 1262-((k*29)%3)*16-((k/7)|0)*9, 19, 13);
      }
      // destra: un pacco solo, intatto, che respira. E' quello buono: crema e nastro verde
      const gl=ctx.createRadialGradient(810,1200,10,810,1200,290);
      gl.addColorStop(0,'rgba(31,184,119,'+(0.16+0.07*Math.sin(t*1.5)).toFixed(3)+')');
      gl.addColorStop(1,'rgba(31,184,119,0)');
      ctx.fillStyle=gl; ctx.globalAlpha=1; ctx.fillRect(540,900,540,600);
      pacco(810, 1200+Math.sin(t*1.1)*7, 1.5, 0.025*Math.sin(t*0.9), 1, '#FBF8F2', '#1FB877');
      ctx.restore();
      velo();
      const c2=document.getElementById('conta20');
      const cp=Math.min(1,Math.max(0,(t-cfg.conta_a)/0.5));
      c2.style.opacity=(cp*(t>SLOG?Math.max(0,1-(t-SLOG)*1.4):1)).toFixed(2);
      document.getElementById('psx').style.color = t>1.0 ? '#FBF8F2' : '#B5A896';
      document.getElementById('pdx').style.color = '#1FB877';
      const via=(t>SLOG?Math.max(0,1-(t-SLOG)*2.2):1).toFixed(2);   // largo allo slogan: spariscono
      for(const id of ['tsx','tdx','psx','pdx'])
        document.getElementById(id).style.opacity=via;
    }
  };
})();
"""

MOTIVO_INTERFACCIA = r"""
// INTERFACCIA — lo schermo non mente: la card di un negozio online, il countdown che
// scade... e riparte da capo. Due volte, perche' una potrebbe sembrare un caso.
// cfg: { prezzo:'89 €', secondi:9, reset:[t1,t2] istanti dei reset, multa_a,
//        multa:'Antitrust · 2.000.000 € di sanzione' }
MOTIVO = (function(){
  const cfg = CFG;
  function resto(t){
    // Con reset: il timer muore proprio quando la voce dice "ecco", poi riparte da capo.
    // Senza reset (cfg.reset assente o vuota): un countdown normale che scorre e basta.
    if(!cfg.reset || !cfg.reset.length) return Math.max(0, cfg.secondi-t);
    const r0=cfg.reset[0];
    if(t<r0) return Math.max(0, r0-t);
    let da=r0; for(const r of cfg.reset){ if(t>=r) da=r; }
    return Math.max(0, cfg.secondi-(t-da));
  }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="card" style="position:absolute;left:110px;right:110px;top:640px;height:880px;'+
        'background:#221B14;border:3px solid rgba(251,248,242,.14);border-radius:34px;overflow:hidden">'+
        '<div style="height:78px;background:rgba(251,248,242,.07);display:flex;align-items:center;padding-left:30px">'+
        '<span style="width:18px;height:18px;border-radius:50%;background:#7D7161;margin-right:12px"></span>'+
        '<span style="width:18px;height:18px;border-radius:50%;background:#7D7161;margin-right:12px"></span>'+
        '<span style="width:18px;height:18px;border-radius:50%;background:#7D7161"></span></div>'+
        '<div style="margin:44px 50px 0;height:250px;border-radius:22px;background:rgba(251,248,242,.08)"></div>'+
        '<div style="margin:34px 50px 0;height:26px;width:60%;border-radius:13px;background:rgba(251,248,242,.14)"></div>'+
        '<div style="margin:18px 50px 0;height:26px;width:42%;border-radius:13px;background:rgba(251,248,242,.10)"></div>'+
        '<div id="pz" style="margin:40px 50px 0;font-family:\'Space Grotesk\';font-weight:700;'+
        'font-size:78px;color:#FBF8F2"></div>'+
        (cfg.pill?'<div id="scars" style="display:inline-block;margin:22px 0 0 50px;'+
        'font-weight:800;font-size:34px;letter-spacing:.5px;color:#16120D;'+
        'background:#B5A896;border-radius:14px;padding:12px 22px"></div><br>':'')+
        '<div id="cd" style="margin:26px 50px 0;display:inline-block;margin-left:50px;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:56px;letter-spacing:1px;'+
        'color:#16120D;background:#FBF8F2;border-radius:18px;padding:14px 30px;'+
        'font-variant-numeric:tabular-nums"></div></div>'+
        '<div id="multa2" style="position:absolute;left:150px;right:150px;top:1372px;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:44px;color:#0A2418;'+
        'background:#1FB877;border-radius:26px;padding:24px 16px;opacity:0"></div>';
      document.getElementById('pz').innerHTML=cfg.prezzo;
      if(cfg.pill) document.getElementById('scars').textContent=cfg.pill;
      document.getElementById('multa2').textContent=cfg.multa;
    },
    draw(t){
      const fin=Math.min(1,Math.max(0,(t-SLOG)/0.8));
      ctx.clearRect(0,0,1080,1920);
      velo();
      const s=resto(t);
      const cd=document.getElementById('cd');
      const mm=String(Math.floor(s/60)).padStart(2,'0'), ss=String(Math.floor(s%60)).padStart(2,'0');
      cd.textContent='Scade tra '+mm+':'+ss;
      // il lampo del reset: e' il momento della verita', va visto
      let flash=0;
      for(const r of cfg.reset){ if(t>=r && t<r+0.5) flash=1-(t-r)/0.5; }
      cd.style.background = flash>0 ? '#1FB877' : (s<2.2 ? '#FBF8F2' : 'rgba(251,248,242,.92)');
      if(cfg.pill){ const sc=document.getElementById('scars');
        sc.style.transform='scale('+(1+0.045*Math.sin(t*3.4))+') rotate('+(0.6*Math.sin(t*2.2))+'deg)'; }
      cd.style.transform='scale('+(1+0.05*flash+(s<2.2?0.02*Math.sin(t*14):0.012*Math.sin(t*2.4))).toFixed(3)+')';
      const card=document.getElementById('card');
      card.style.transform='translateY('+(Math.sin(t*1.05)*7).toFixed(1)+'px) scale('+
        (1+0.012*Math.sin(t*0.85)+0.02*fin*Math.sin(t*1.3)).toFixed(3)+') rotate('+(0.3*Math.sin(t*0.7)).toFixed(2)+'deg)';
      const m=document.getElementById('multa2');
      const mp=Math.min(1,Math.max(0,(t-cfg.multa_a)/0.45));
      m.style.opacity=(mp*(t>SLOG+0.6?Math.max(0.55,1-(t-SLOG-0.6)):1)).toFixed(2);
      m.style.transform='scale('+(0.85+0.15*ease(mp)+0.012*Math.sin(t*2.2)).toFixed(3)+')';
      cd.style.opacity=(1-mp*0.85).toFixed(2);      // il timer lascia il posto alla multa
      card.style.opacity=(t>SLOG?Math.max(0.25,1-(t-SLOG)*1.2):1).toFixed(2);
    }
  };
})();
"""

MOTIVO_DOMANDA = r"""
// DOMANDA — impianto tipografico per la rubrica R3: al centro non c'e' un numero ma
// l'esca stessa ("ULTIMI 2 PEZZI"), che pulsa come sui siti; poi i 37 studi si accendono
// come una giuria, e alla fine l'esca si moltiplica: la vedi ovunque perche' funziona.
// cfg: { pill:'ULTIMI 2 PEZZI', dots_a, dots_n:37, replica_a }
MOTIVO = (function(){
  const cfg = CFG;
  let seed=53; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
  const ORD=[]; for(let i=0;i<cfg.dots_n;i++) ORD.push(rnd());
  const REP=[]; for(let i=0;i<6;i++) REP.push({dy:i*105, dx:(i%2?36:-36), o:rnd()*0.25});
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="qmark" style="position:absolute;top:610px;left:0;right:0;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:300px;color:#1FB877;opacity:0">?</div>'+
        '<div id="pills" style="position:absolute;top:940px;left:0;right:0"></div>';
      let h='';
      for(let i=0;i<7;i++) h+='<div class="pl"></div>';
      document.getElementById('pills').innerHTML=
        '<style>.pl{position:absolute;left:0;right:0;margin:0 auto;width:640px;text-align:center;'+
        "font-family:Manrope;font-weight:800;font-size:54px;letter-spacing:2px;color:#16120D;"+
        'background:#FBF8F2;border-radius:60px;padding:26px 0}</style>'+h;
      const P=document.querySelectorAll('.pl');
      P.forEach(el=>el.textContent=cfg.pill);
    },
    draw(t){
      const fin=Math.min(1,Math.max(0,(t-SLOG)/0.8));
      ctx.clearRect(0,0,1080,1920);
      // i 37 studi: una griglia di tacche che si accendono una a una
      const dp=Math.min(1,Math.max(0,(t-cfg.dots_a)/2.2));
      const zoom=1+0.05*(t/DUR)+0.02*Math.sin(t*1.15)*fin;
      ctx.save(); ctx.translate(540,1300); ctx.scale(zoom,zoom); ctx.translate(-540,-1300);
      const acc=Math.round(cfg.dots_n*ease(dp));
      for(let i=0;i<cfg.dots_n;i++){
        const c=i%13, r=(i/13)|0;
        const on = i<acc;
        ctx.globalAlpha = on ? 0.95 : 0.18;
        ctx.fillStyle = on ? '#1FB877' : '#B5A896';
        const puls = on ? 1+0.10*Math.sin(t*2.2+i*1.7) : 1;
        ctx.fillRect(198+c*54, 1398-((r+1)*46)*1, 14*puls, 34*puls);
      }
      if(dp>0){
        ctx.globalAlpha=Math.min(1,dp*2); ctx.fillStyle='#B5A896';
        ctx.font='800 30px Manrope'; ctx.textAlign='left';
        ctx.fillText('37 studi · 335 misure', 198, 1452);
      }
      ctx.restore();
      velo();
      // l'esca che pulsa, poi si moltiplica
      const P=document.querySelectorAll('.pl');
      const rp=ease(Math.min(1,Math.max(0,(t-cfg.replica_a)/1.1)));
      P.forEach((el,i)=>{
        if(i===0){
          el.style.opacity=(t>SLOG?Math.max(0.2,1-(t-SLOG)*1.3):1).toFixed(2);
          el.style.transform='scale('+(1+0.045*Math.sin(t*3.1))+')';
        } else {
          const OFF=[-105,105,-210,210,-315,-420];   // giu' massimo due file: sotto ci sono le tacche
          const r=REP[i-1];
          el.style.opacity=(rp*(0.45-r.o*0.3)*(t>SLOG?Math.max(0.06,1-(t-SLOG)*2.2):1)).toFixed(2);
          el.style.transform='translate('+(r.dx*rp)+'px,'+(OFF[i-1]*rp)+'px) scale('+(1-0.045*Math.ceil(i/2))+')';
        }
      });
      const q=document.getElementById('qmark');
      const qp=Math.min(1,t/0.5);
      q.style.opacity=((t<cfg.dots_a?qp:Math.max(0,1-(t-cfg.dots_a)*1.2))* (t>SLOG?0:1)).toFixed(2);
      q.style.transform='scale('+(0.7+0.3*ease(qp)+0.03*Math.sin(t*1.9)).toFixed(3)+') rotate('+(4*Math.sin(t*1.1)).toFixed(1)+'deg)';
    }
  };
})();
"""

MOTIVO_VETRINE = r"""
// VETRINE — una via di negozi in saldo, l'ispezione passa, uno su tre viene verbalizzato.
// La griglia e' 30 vetrine e i verbali sono ESATTAMENTE 10: il rapporto detto a voce si
// deve poter contare sul fotogramma fermo.
// cfg: { scan_a, scan_fine, chip_a, chip:"1 su 3" }
MOTIVO = (function(){
  const cfg = CFG;
  let seed=61; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
  const COLS=6, ROWS=5, X0=118, Y0=724, DX=142, DY=142, W=110, H=104;
  const S=[];
  // Gli irregolari sono ESATTI ma sparsi (mai colonne allineate: il pattern si vede).
  const IRR=new Set(cfg.flag||[1,4,8,11,12,17,20,21,27,28]);
  for(let i=0;i<COLS*ROWS;i++){
    S.push({x:X0+(i%COLS)*DX, y:Y0+((i/COLS)|0)*DY,
            irr:IRR.has(i),
            ph:rnd()*6.283, j:(rnd()-.5)*8});
  }
  function negozio(o,acceso,flag,t){
    const x=o.x+o.j, y=o.y+Math.sin(t*0.9+o.ph)*2.5;
    ctx.globalAlpha = acceso ? 0.9 : 0.32;
    ctx.strokeStyle='#B5A896'; ctx.lineWidth=3;
    ctx.strokeRect(x,y+26,W,H-26);                              // il corpo
    ctx.fillStyle='rgba(251,248,242,'+(acceso?0.14:0.05)+')';
    ctx.fillRect(x+14,y+44,W-28,H-58);                          // la vetrina
    if(cfg.stile==='siti'){                                      // finestra browser
      ctx.fillStyle='rgba(251,248,242,'+(acceso?0.22:0.08)+')';
      ctx.fillRect(x,y+2,W,22);
      ctx.fillStyle='#16120D';
      for(let k=0;k<3;k++){ ctx.globalAlpha=(acceso?0.9:0.4);
        ctx.beginPath(); ctx.arc(x+12+k*14,y+13,4,0,6.2832); ctx.fill(); }
    } else {
      ctx.fillStyle='#B5A896';
      for(let k=0;k<4;k++){                                      // la tenda a strisce
        ctx.globalAlpha=(acceso?0.9:0.32)*(k%2?0.45:0.95);
        ctx.fillRect(x-4+k*(W+8)/4, y+8, (W+8)/4-3, 20);
      }
    }
    if(flag){                                                    // il verbale: verde, storto
      ctx.save(); ctx.translate(x+W/2,y+70); ctx.rotate(-0.12);
      ctx.globalAlpha=0.95; ctx.fillStyle='#1FB877';
      ctx.fillRect(-44,-22,88,44);
      ctx.fillStyle='#0A2418'; ctx.font='800 22px Manrope'; ctx.textAlign='center';
      ctx.fillText(cfg.tag||'VERBALE',0,8); ctx.restore();
    }
  }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="chip" style="position:absolute;top:562px;left:0;right:0;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:150px;letter-spacing:-6px;'+
        'color:#1FB877;opacity:0;text-shadow:0 20px 70px rgba(22,18,13,.95)"></div>';
      document.getElementById('chip').textContent=cfg.chip;
    },
    draw(t){
      const fin=Math.min(1,Math.max(0,(t-SLOG)/0.8));
      const zoom=1+0.05*(t/DUR)+0.02*Math.sin(t*1.2)*fin;
      ctx.save(); ctx.translate(540,1080); ctx.scale(zoom,zoom); ctx.translate(-540,-1080);
      // l'ispezione: una linea che scorre la via, negozio per negozio
      const p=Math.min(1,Math.max(0,(t-cfg.scan_a)/(cfg.scan_fine-cfg.scan_a)));
      const passo=p*COLS*ROWS;
      for(let i=0;i<S.length;i++){
        // ordine di lettura: riga per riga, da sinistra
        negozio(S[i], i<passo, S[i].irr && i<passo-0.5, t);
      }
      if(p>0 && p<1){                                            // la linea dell'ispezione
        const i=Math.floor(passo), r=(i/COLS)|0, c=i%COLS;
        const lx=X0+c*DX+(passo-i)*DX-16, ly=Y0+r*DY;
        ctx.globalAlpha=0.85; ctx.strokeStyle='#1FB877'; ctx.lineWidth=4;
        ctx.setLineDash([10,8]); ctx.lineDashOffset=-t*30;
        ctx.beginPath(); ctx.moveTo(lx,ly-8); ctx.lineTo(lx,ly+H+14); ctx.stroke();
        ctx.setLineDash([]);
      }
      ctx.restore();
      velo();
      const ch=document.getElementById('chip');
      const cp=Math.min(1,Math.max(0,(t-cfg.chip_a)/0.4));
      ch.style.opacity=(cp*(t>SLOG?Math.max(0,1-(t-SLOG)*1.8):1)).toFixed(2);
      ch.style.transform='scale('+(0.8+0.2*ease(cp)+0.015*Math.sin(t*2.1)).toFixed(3)+')';
    }
  };
})();
"""

MOTIVO_CENTO = r"""
// CENTO — una griglia 10x10. La voce chiede "su cento, quanti?", e se ne accendono
// POCHI, esatti e sparsi. Il vuoto che resta e' il messaggio.
// cfg: { acc:[indici degli accesi], accendi_a, chip:"al massimo 5 su 100", chip_a }
MOTIVO = (function(){
  const cfg = CFG;
  let seed=71; function rnd(){seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;}
  const N=100, COLS=10, X0=120, Y0=742, DX=94, DY=78;
  const D=[];
  for(let i=0;i<N;i++) D.push({x:X0+(i%COLS)*DX, y:Y0+((i/COLS)|0)*DY,
                               ph:rnd()*6.283, ord:rnd()});
  const ACC=cfg.acc||[7,23,41,68,84];
  function divano(x,y,on,t,al){
    ctx.globalAlpha=al;
    ctx.fillStyle = on ? '#1FB877' : '#B5A896';
    ctx.fillRect(x, y+18, 64, 22);                 // seduta
    ctx.fillRect(x, y, 64, 14);                    // schienale
    ctx.fillRect(x-8, y+8, 10, 32);                // braccioli
    ctx.fillRect(x+62, y+8, 10, 32);
  }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="chipc" style="position:absolute;top:560px;left:0;right:0;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:96px;letter-spacing:-3px;'+
        'color:#1FB877;opacity:0;text-shadow:0 20px 70px rgba(22,18,13,.95)"></div>';
      document.getElementById('chipc').textContent=cfg.chip;
    },
    draw(t){
      const fin=Math.min(1,Math.max(0,(t-SLOG)/0.8));
      const zoom=1+0.05*(t/DUR)+0.02*Math.sin(t*1.2)*fin;
      ctx.save(); ctx.translate(540,1080); ctx.scale(zoom,zoom); ctx.translate(-540,-1080);
      const ent=Math.min(1,t/1.4);                 // la griglia entra a onde
      for(let i=0;i<N;i++){
        const d=D[i];
        if(d.ord>ent) continue;
        const on = ACC.includes(i) && t>cfg.accendi_a+ACC.indexOf(i)*0.22;
        const br=Math.sin(t*0.9+d.ph)*2;
        divano(d.x, d.y+br, on, t, on?0.95:(0.30+0.05*Math.sin(t*1.1+d.ph)));
        if(on){ ctx.globalAlpha=0.25+0.1*Math.sin(t*2.5+d.ph);   // alone dei pochi veri
          ctx.fillStyle='#1FB877'; ctx.fillRect(d.x-14,d.y+br-8,92,56); }
      }
      ctx.restore();
      velo();
      const ch=document.getElementById('chipc');
      const cp=Math.min(1,Math.max(0,(t-cfg.chip_a)/0.4));
      ch.style.opacity=(cp*(t>SLOG?Math.max(0,1-(t-SLOG)*1.8):1)).toFixed(2);
      ch.style.transform='scale('+(0.85+0.15*ease(cp)+0.014*Math.sin(t*2.1)).toFixed(3)+')';
    }
  };
})();
"""

MOTIVO_TEMPO = r"""
// TEMPO — una linea del tempo: un paese si muove per primo, gli altri arrivano anni dopo.
// cfg: { anni:[2021,...,2027], da:2022, a:2026, et_da:"Francia", et_a:"Unione Europea",
//        da_t, corsa_t, a_t, chip:"4 anni prima", chip_a }
MOTIVO = (function(){
  const cfg = CFG;
  const X0=120, X1=960, Y=1120;
  function px(anno){ return X0+(X1-X0)*(anno-cfg.anni[0])/(cfg.anni[cfg.anni.length-1]-cfg.anni[0]); }
  return {
    init(){
      document.getElementById('mezzo').innerHTML =
        '<div id="chipt" style="position:absolute;top:588px;left:0;right:0;text-align:center;'+
        'font-family:\'Space Grotesk\';font-weight:700;font-size:110px;letter-spacing:-4px;'+
        'color:#1FB877;opacity:0;text-shadow:0 20px 70px rgba(22,18,13,.95)"></div>';
      document.getElementById('chipt').textContent=cfg.chip;
    },
    draw(t){
      const fin=Math.min(1,Math.max(0,(t-SLOG)/0.8));
      const zoom=1+0.05*(t/DUR)+0.02*Math.sin(t*1.2)*fin;
      ctx.save(); ctx.translate(540,1080); ctx.scale(zoom,zoom);
      ctx.rotate(0.006*Math.sin(t*1.05)*fin); ctx.translate(-540,-1080);
      // l'asse e gli anni
      ctx.globalAlpha=0.6; ctx.strokeStyle='#7D7161'; ctx.lineWidth=4;
      ctx.beginPath(); ctx.moveTo(X0,Y); ctx.lineTo(X1,Y); ctx.stroke();
      ctx.font='600 30px Manrope'; ctx.textAlign='center'; ctx.fillStyle='#7D7161';
      for(const a of cfg.anni){
        ctx.globalAlpha=0.7;
        ctx.beginPath(); ctx.moveTo(px(a),Y-12); ctx.lineTo(px(a),Y+12); ctx.stroke();
        ctx.fillText(String(a), px(a), Y+56);
      }
      const p1=ease(Math.min(1,Math.max(0,(t-cfg.da_t)/0.5)));
      const run=ease(Math.min(1,Math.max(0,(t-cfg.corsa_t)/(cfg.a_t-cfg.corsa_t))));
      const p2=ease(Math.min(1,Math.max(0,(t-cfg.a_t)/0.5)));
      if(run>0){                                   // la corsa fra i due punti
        ctx.globalAlpha=0.9; ctx.strokeStyle='#1FB877'; ctx.lineWidth=9; ctx.lineCap='round';
        ctx.setLineDash([16,12]); ctx.lineDashOffset=-t*26;
        ctx.beginPath(); ctx.moveTo(px(cfg.da),Y);
        ctx.lineTo(px(cfg.da)+(px(cfg.a)-px(cfg.da))*run, Y); ctx.stroke(); ctx.setLineDash([]);
      }
      function nodo(anno,et,pp,sotto){
        if(pp<=0) return;
        const x=px(anno), pulse=1+0.10*Math.sin(t*2.4)*pp;
        ctx.globalAlpha=pp; ctx.fillStyle='#1FB877';
        ctx.beginPath(); ctx.arc(x,Y,20*pulse*pp,0,6.2832); ctx.fill();
        ctx.globalAlpha=0.3*pp; ctx.beginPath(); ctx.arc(x,Y,38*pulse,0,6.2832); ctx.fill();
        ctx.globalAlpha=pp; ctx.fillStyle='#FBF8F2';
        ctx.font='800 38px Manrope';
        ctx.fillText(et, x, sotto? Y+120 : Y-96);
        ctx.font='700 44px "Space Grotesk"';
        ctx.fillText(String(anno), x, sotto? Y+170 : Y-46);
      }
      nodo(cfg.da, cfg.et_da, p1, false);
      nodo(cfg.a, cfg.et_a, p2, true);
      ctx.restore();
      velo();
      const ch=document.getElementById('chipt');
      const cp=Math.min(1,Math.max(0,(t-cfg.chip_a)/0.4));
      ch.style.opacity=(cp*(t>SLOG?Math.max(0,1-(t-SLOG)*1.8):1)).toFixed(2);
      ch.style.transform='scale('+(0.85+0.15*ease(cp)+0.014*Math.sin(t*2.1)).toFixed(3)+')';
    }
  };
})();
"""
MOTIVI = {"folla": MOTIVO_FOLLA, "conto": MOTIVO_CONTO, "pila": MOTIVO_PILA,
          "contatore": MOTIVO_CONTATORE, "grafico": MOTIVO_GRAFICO,
          "cartellino": MOTIVO_CARTELLINO, "confronto": MOTIVO_CONFRONTO,
          "interfaccia": MOTIVO_INTERFACCIA, "domanda": MOTIVO_DOMANDA, "vetrine": MOTIVO_VETRINE,
          "cento": MOTIVO_CENTO, "tempo": MOTIVO_TEMPO}

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
  // Il velo alto separa il testo dalla folla nei motivi "densi" (folla, conto). Nei motivi
  // a oggetto centrale (cartellino, card...) taglierebbe l'oggetto a meta': si spegne
  // dalla spec con "velo_alto": false. Trovato sul timbro MAI ESISTITO, oscurato a meta'.
  ctx.globalAlpha=1;
  if(CFG.velo_alto!==false){
    const vg=ctx.createLinearGradient(0,1010,0,1420);
    vg.addColorStop(0,'rgba(22,18,13,.92)'); vg.addColorStop(1,'rgba(22,18,13,0)');
    ctx.fillStyle=vg; ctx.fillRect(0,1010,1080,410);
  }
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

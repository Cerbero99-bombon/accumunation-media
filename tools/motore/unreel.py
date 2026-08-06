# -*- coding: utf-8 -*-
"""Un reel intero, da copione a file finito, in una chiamata sola.

I tempi della grafica NON si riscrivono a mano quando cambia la voce: si deformano.
`ritempra` prende i tempi della spec vecchia e li rimappa sulla nuova voce frase per
frase (deformazione lineare a tratti). Cosi' cambiando voce o copione la regia resta
agganciata al parlato invece di scivolare, che e' il difetto che si vede subito.

  python3 unreel.py <lavoro.json>
"""
import json, subprocess, sys, os, pathlib

FAB = "/home/user/fab"
CHIAVI = {          # quali numeri della cfg sono tempi, spec per spec
 "spec-burberry":   ["conta_da", "conta_a", "evid.a"],
 "spec-cartellino": ["strappo_a", "multa_a"],
 "spec-cento":      ["accendi_a", "chip_a"],
 "spec-confronto":  ["conta_a"],
 "spec-contatore":  ["conta_da", "conta_a", "evid.a"],
 "spec-conto":      ["zero_a", "pill_a", "muro_a", "evid_a"],
 "spec-domanda":    ["dots_a", "replica_a"],
 "spec-edreams":    ["multa_a"],
 "spec-francia":    ["da_t", "corsa_t", "a_t", "chip_a"],
 "spec-grafico":    ["disegna_a", "legge_a", "falso_a", "trema_a"],
 "spec-interfaccia":["multa_a", "reset[]"],
 "spec-marion":     ["strappo_a", "multa_a"],
 "spec-pila":       ["distru_a", "vieta_a"],
 "spec-trucchi":    ["scan_a", "scan_fine", "chip_a"],
 "spec-vetrine":    ["scan_a", "scan_fine", "chip_a"],
 "spec-moto":       ["soglie[].t"],
}


def sh(c, mostra=False):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode:
        print("COMANDO FALLITO:", c[:200]); print(r.stderr[-1200:]); raise SystemExit(1)
    if mostra and r.stdout.strip(): print(r.stdout.strip())
    return r.stdout.strip()


def inizi(parole):
    s = {}
    for a, b, t, i in parole:
        s.setdefault(i, a)
    return [s[k] for k in sorted(s)]


def deforma(v, vecchi, nuovi, vd, nd):
    """Porta l'istante v dai tempi vecchi ai nuovi, frase per frase."""
    if v is None or v > vd + 0.5:
        return v                                    # sentinelle tipo 99 = mai
    a = list(vecchi) + [vd]; b = list(nuovi) + [nd]
    for i in range(len(a) - 1):
        if a[i] <= v <= a[i + 1]:
            k = (v - a[i]) / max(1e-6, a[i + 1] - a[i])
            return round(b[i] + k * (b[i + 1] - b[i]), 2)
    return round(v * nd / vd, 2)


def ritempra(cfg, chiavi, f):
    for k in chiavi:
        if k.endswith("[]"):
            n = k[:-2]
            if n in cfg: cfg[n] = [f(x) for x in cfg[n]]
        elif "[]." in k:
            n, campo = k.split("[].")
            for el in cfg.get(n, []): el[campo] = f(el[campo])
        elif "." in k:
            n, campo = k.split(".")
            if n in cfg and campo in cfg[n]: cfg[n][campo] = f(cfg[n][campo])
        elif k in cfg:
            cfg[k] = f(cfg[k])
    return cfg


def main(lav):
    L = json.load(open(lav, encoding="utf-8"))
    nome, spec_nome = L["nome"], L["spec"]
    d = pathlib.Path("/home/user/lav") / nome
    d.mkdir(parents=True, exist_ok=True)
    os.chdir(d)

    json.dump(L["copione"], open("copione.json", "w"), ensure_ascii=False)
    sh(f'python3 {FAB}/tools/motore/voce.py copione.json voce.wav words.json', True)

    vecchia = json.load(open(f"{FAB}/tools/stileD/{spec_nome}.json", encoding="utf-8"))
    nuove = json.load(open("words.json", encoding="utf-8"))
    vi, ni = inizi(vecchia["parole"]), inizi(nuove)
    if len(vi) != len(ni):
        print(f"ATTENZIONE: la spec vecchia ha {len(vi)} frasi, il copione nuovo {len(ni)}.")
    vd, nd = vecchia["durata"], round(nuove[-1][1] + 0.9, 2)
    f = lambda v: deforma(v, vi, ni, vd, nd)

    s = dict(vecchia)
    s["parole"] = nuove
    s["durata"] = nd
    s["slogan_da"] = round(ni[-1] - 0.25, 2)
    s["fonte_da"] = 0.6
    s["cfg"] = ritempra(dict(vecchia["cfg"]), CHIAVI[spec_nome], f)
    s["font_root"] = f"{FAB}/tools/assets/fonts"
    s["logo_path"] = f"{FAB}/tools/assets/logo/logo-an.png"
    json.dump(s, open("spec.json", "w"), ensure_ascii=False)
    print("durata", nd, "| slogan_da", s["slogan_da"], "| cfg", json.dumps(s["cfg"], ensure_ascii=False)[:220])

    sh(f'python3 {FAB}/tools/stileD/motore.py spec.json pagina.html')
    sh(f'python3 {FAB}/tools/stileD/shoot.py pagina.html . {nd}', True)
    sh('ffmpeg -y -loglevel error -framerate 30 -i _f/f%05d.jpg -c:v libx264 -preset veryfast -crf 20 '
       '-pix_fmt yuv420p -g 15 -keyint_min 15 -sc_threshold 0 -movflags +faststart muto.mp4')
    mus = L.get("musica", "cipher2_31s.m4a")
    sh(f'ffmpeg -y -loglevel error -i voce.wav -stream_loop -1 -i {FAB}/tools/assets/music/{mus} -filter_complex '
       f'"[0:a]acompressor=threshold=0.125:ratio=3:makeup=2,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[vo];'
       f'[1:a]atrim=0:{nd},volume=0.55,afade=t=in:st=0:d=0.6,afade=t=out:st={nd-0.84:.2f}:d=0.84,'
       f'aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[mu];'
       f'[mu][vo]sidechaincompress=threshold=0.05:ratio=6:attack=10:release=350[mud];'
       f'[vo][mud]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1:LRA=9[mix]" -map "[mix]" -ar 48000 -ac 2 mix.wav')
    sh('ffmpeg -y -loglevel error -i muto.mp4 -i mix.wav -c:v copy -c:a aac -b:a 160k -shortest corpo.mp4')
    sh(f'python3 {FAB}/tools/motore/spezzone.py /home/user/hooks/{L["hook"]}.mp4 corpo.mp4 '
       f'{nome}.mp4 {L["transizione"]} {L.get("inizio_hook","")}'.strip(), True)
    sh(f'ffmpeg -y -loglevel error -ss {L.get("cover_a", 3.0)} -i {nome}.mp4 -frames:v 1 -q:v 3 {nome}-cover.jpg')
    print("FATTO", d / f"{nome}.mp4")


main(sys.argv[1])

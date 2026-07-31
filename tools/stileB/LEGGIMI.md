# Stile B — "Numeri vivi"

Il protagonista e' **un numero che si muove**, non il testo. Serve per le rubriche dove esiste una
cifra vera da mostrare: R1 (Il conto in 10 secondi), R5 (Dietro il prezzo pieno), R2 quando la
traduzione ha un numero dentro.

## Come si fa un reel

1. **Voce** — sulla macchina con rete (`COMPOSIO_REMOTE_BASH_TOOL`), perche' dal container
   l'endpoint Microsoft e' irraggiungibile:
   `pip install edge-tts` poi `tools/tts_edge.py "testo" voce.mp3 words.json`,
   `ffmpeg -i voce.mp3 -ar 48000 -ac 1 voce.wav`, e commit in `tools/assets/vo/`.
   `words.json` da' i **tempi parola per parola gratis**: i sottotitoli sono esatti, senza trascrizione.
2. **Scene** — si scrive `spec.json`: ogni scena ha `a` e `b` (secondi), presi **dai tempi delle
   parole**, non a occhio. Campi: `kick`, `h1` (con `<em>` per il verde), `sub`, `prezzo` (col taglio
   rosso animato), `count` + `suffisso` (+ `numsize` se il numero e' lungo), `bar`.
3. **Sottotitoli** — si raggruppano le parole in frasi da 4-6, ogni gruppo compare intero con la
   parola corrente in verde. Mai piu' di 6 parole per gruppo.
4. **Fotogrammi** — `python3 shoot.py out.html <dir> <durata>`: pilota la pagina con `setT(t)`,
   uno scatto per fotogramma a 30fps. Deterministico: stesso input, stesso video.
5. **Audio** — musica CC da `tools/assets/music/`, ducking e loudnorm a due passate:

       ffmpeg -y -i MUSICA -i VOCE -filter_complex \
       "[1:a]highpass=f=80,acompressor=threshold=0.125:ratio=3:attack=10:release=200:makeup=2[voc];\
        [voc]asplit=2[vo][key];[0:a]atrim=0:DUR,volume=-7dB,afade=t=out:st=DUR-1.5:d=1.5[mus];\
        [mus][key]sidechaincompress=threshold=0.05:ratio=6:attack=10:release=350[duck];\
        [duck][vo]amix=inputs=2:duration=first:normalize=0[mix]" -map "[mix]" mix.wav

   Poi loudnorm misurato e riapplicato: si arriva a **-14 LUFS**, lo standard dei social.
   `makeup=2` e `normalize=0` non sono opzionali: senza, la voce sparisce sotto la musica.
6. **Copertina** — stessa spec con una scena sola e durata 1: esce un JPEG 9:16 con il gancio.

## Trappole gia' pagate

- `data-cut` va sull'elemento `<i class="taglio">`, non sul contenitore: altrimenti la riga rossa
  non appare mai e non te ne accorgi finche' non guardi i fotogrammi.
- I contatori vanno presi con `querySelectorAll`, non `querySelector`: col secondo, il secondo
  numero del reel resta fermo a zero.
- Numeri lunghi (1.000.000) vanno a capo e si tagliano: serve `numsize` piu' piccolo e `nowrap`.
- Dissolvenza fra scene: **0.16s**, non 0.35. Con 0.35 due scene si sovrappongono e si legge doppio.
- **Guardare sempre i fotogrammi** montati a provino prima di esportare. Tutti e quattro i difetti
  sopra sono usciti da li', nessuno dal codice.

## Cosa resta a mano

L'audio in trend di Instagram. Muxare una traccia **non e'** taggare un audio in trend: il reel non
entra nella pagina del suono. Si sceglie reel per reel: autonomia (musica nostra) o distribuzione
(video con la sola voce e traccia messa a mano dall'app).

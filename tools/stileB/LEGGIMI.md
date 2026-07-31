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

## Sottotitoli: mai ripetere cio' che e' gia' scritto

Ogni scena dichiara il proprio testo visibile (`h1`, `sub`, `kick`, `prezzo`), ripulito da tag e
punteggiatura. Prima di mostrare un gruppo di sottotitolo, il template confronta le sue parole piene
(piu' di 2 lettere) con quello che in quell'istante e' gia' sullo schermo: **se meta' o piu' sono
gia' scritte, il sottotitolo tace**. Il risultato e' che il testo grande e il sottotitolo si
alternano invece di sovrapporsi, e lo schermo non dice mai due volte la stessa cosa.

Regola pratica quando si scrive una spec: se una scena ha un `h1` che e' quasi il parlato, non
metterci anche il `sub` che lo ripete. Il filtro copre l'errore, ma una scena scritta bene non ne
ha bisogno.

## Espressivita': si ottiene dalla regia, non dalla voce

Una voce sintetica letta tutta d'un fiato suona piatta, e se la si accelera suona enfatica: sono i
due modi in cui si capisce che e' finta. La soluzione non e' cercare una voce migliore, e' **dirigere
la lettura**. `vox.py` legge **una frase alla volta**, e ogni frase ha:

- il suo **ritmo** (`rate`): la frase chiave va lenta, quella di servizio va normale;
- il suo **tono** (`pitch`): si scende sui punti che devono pesare;
- la sua **pausa dopo** (`pausa`): il silenzio prima di un numero vale piu' di qualsiasi enfasi.

Esempio dal primo reel: "Zero." letta a **-22%** e **-10Hz**, con 0.55 secondi di silenzio prima e
dopo. Da sola quella parola occupa un secondo di video e non serve nient'altro.

I blocchi vengono poi cuciti con i silenzi veri, e `words.json` esce con i **tempi assoluti gia'
corretti**: le scene si agganciano a quelli, quindi il montaggio resta sincronizzato anche se si
cambia il ritmo di una frase sola.

Regola pratica: **un blocco = una frase = un gruppo di sottotitolo**. Cosi' i tre livelli (voce,
testo grande, sottotitolo) sono d'accordo per costruzione.

Voce scelta: `fr-FR-RemyMultilingualNeural`. Per le parole che una voce non italiana storpia si
scrive la grafia che la fa leggere giusta (es. `l'anti-trust` invece di `l'antitrust`).

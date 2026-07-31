# Stile D — "Movimento continuo"

Non e' una sequenza di immagini con le dissolvenze: e' **una sola inquadratura che si muove per
tutta la durata**. Nasce dalla critica di Enrico agli stili precedenti, che erano slideshow scritte
bene ma restavano slideshow.

## L'idea visiva

E' il meccanismo stesso di Accumunation, mostrato invece che raccontato: **le persone si accumulano
dal basso e il prezzo scende fisicamente verso di loro**. Nessun taglio, nessuna dissolvenza.
Chi guarda capisce prima di leggere.

- La folla e' disegnata su canvas: 500 figure che entrano dal basso con traiettorie e ritardi
  diversi. **Serve la prospettiva**: la fila davanti grande e opaca, quelle dietro sempre piu'
  piccole e velate (scala e passo che calano del 7% a fila). Senza, si legge come una texture
  verde e non come gente.
- La folla entra **dal centro verso i lati**, fila per fila: si aggrega attorno alla prima persona.
  Se entra da un capo, i primi secondi hanno gente in un angolo e il resto vuoto.
- Il prezzo e' un elemento che **cambia posizione**, non solo valore: parte in alto e scende
  addosso alla folla. Deve fermarsi sopra la folla, mai dentro.
- La camera spinge, e spinge **di piu' nella seconda meta'**, quando la folla e' completa.
- Il testo entra **a frasi**, con accesa la parola che la voce sta pronunciando in quell'istante.
  A parola singola sembra un sottotitolo smarrito.

## Le tre trappole gia' pagate (revisione v2, 31/07/2026)

Tutte e tre sono uscite **guardando i fotogrammi**, nessuna dal codice.

1. **Palette sbagliata.** La v1 era su navy `#0b1220`, cioe' esattamente l'errore del 28/07 gia'
   scritto in `references/brand.md`. Il fondo social e' il carbone **caldo** `#16120D`, testo crema
   `#FBF8F2`, verde `#1FB877`. Prima di scrivere un colore a mano, rileggere quel file.
2. **Il vuoto.** La folla arrivava a meta' schermo e sotto restava un buco nero per tutto il reel.
   La folla deve salire fino a ~1200 e il prezzo scendere a incontrarla.
3. **Il video fermo dopo il settimo secondo.** Le soglie portano a 500 quando la voce dice
   "cinquecento", cioe' a 7 secondi su 17: da li' in poi, senza contromisure, non si muove piu'
   niente. Servono il **respiro** delle figure (oscillazione lentissima, ~2.6px), la spinta di
   camera che accelera e il prezzo che continua a calare di posizione fino all'ultimo fotogramma.

Regola generale: montare un provino a contatto di 12 fotogrammi e **guardarlo**, poi un crop a
piena risoluzione della zona folla. A 340px di anteprima la prospettiva non si giudica.

## Il ritmo lo detta il parlato

Le soglie della folla (`soglie` nella spec) sono agganciate ai tempi delle parole, non scelte a
occhio: la folla parte quando la voce dice "guarda cosa succede" e finisce quando dice
"cinquecento". Se il video non segue il parlato, l'occhio se ne accorge subito anche senza capire
perche'.

Il campo `parole` della spec e' **`words.json` tal quale**, quarto campo compreso: e' l'indice di
frase, e serve a raggruppare il testo a schermo. Non va tolto.

## Numeri a schermo

Il prezzo segue la scala canonica **100 / 85 / 72 / 62**, dentro la banda R-025. Il contatore di
persone e' un esempio del meccanismo, non traction: in alto a destra resta fissa la dicitura
**"esempio illustrativo"**, che e' l'equivalente del campo `note` dei caroselli. Non toglierla.

## Come si monta

    python3 tools/stileD/moto.py tools/stileD/spec-moto.json out.html
    python3 tools/stileD/shoot.py out.html <dir> <durata>       # ~48s per 17 secondi di video
    # video muto dai frame a 30fps, poi la catena audio di tools/stileB/LEGGIMI.md
    # (ducking sidechain + loudnorm a due passate -> -14 LUFS)

I sottotitoli bruciati **non servono**: il testo grande e' gia' a schermo e sincronizzato. Montare
anche `subs.ass` fa dire due volte la stessa cosa.

## Durata

**Sotto i 20 secondi.** Enrico considera 30+ un'eccezione, non la norma. Un copione da 6 frasi
corte con pause da 0.12-0.32 secondi sta in 17 secondi e non annoia. Le pause lunghe da "regia
teatrale" (0.8s) rallentano il video e vanno usate solo dove il silenzio e' il contenuto.

## Copertina

JPEG 9:16 a parte, non un fotogramma del video: il primo fotogramma e' quasi vuoto per costruzione.
Qui il colore **puo' stonare** col dark del feed, e' voluto (fondo verde pieno, testo inchiostro),
purche' restino il marchio e il carattere. Gancio in due righe con i due prezzi.

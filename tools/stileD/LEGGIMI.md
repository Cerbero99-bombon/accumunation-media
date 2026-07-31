# Stile D — "Movimento continuo"

Non e' una sequenza di immagini con le dissolvenze: e' **una sola inquadratura che si muove per
tutta la durata**. Nasce dalla critica di Enrico agli stili precedenti, che erano slideshow
scritte bene ma restavano slideshow.

**Le regole complete di contenuto e qualita' stanno in `tools/CANONE-REEL.md`.**
**Il cancello automatico e' `tools/collaudo.py`: nessun reel si consegna senza PASS.**

## Com'e' fatto

`motore.py` e' lo scheletro unico: palette calda del brand, testo del parlato a frasi con la
parola pronunciata accesa, riga della fonte, chiusura slogan + dominio, zone sicure di
Instagram, camera che spinge. Quello che cambia da reel a reel e' il **motivo**, un blocco JS
registrato dentro `motore.py`:

| Motivo | Cosa si muove | Quando usarlo |
|---|---|---|
| `folla` | le persone si accumulano, il prezzo scende loro addosso | il meccanismo di Accumunation (spec: `spec-moto.json`) |
| `conto` | un countdown scade, non succede niente, poi il muro dei countdown a zero | urgenza finta, dark pattern (spec: `spec-conto.json`) |

Un reel nuovo su un fatto nuovo = di solito **una spec nuova** su un motivo esistente.
Un motivo nuovo si scrive quando il fatto ha una meccanica visiva diversa (una timeline, un
confronto a due colonne...). Interfaccia: `init()` + `draw(t)`, con `CFG`, `ctx`, `ease`,
`easeIO`, `velo()` gia' disponibili.

## Il rito

    python3 tools/stileD/motore.py spec.json out.html
    python3 tools/stileD/shoot.py out.html <dir> <durata>     # ~50s per 20s di video
    # audio: catena di tools/stileB/LEGGIMI.md (ducking + loudnorm 2 passate -> -14 LUFS)
    python3 tools/collaudo.py FINAL.mp4 words.json --cover cover.jpg
    # PASS -> guardare COMUNQUE il provino a contatto -> consegna

I sottotitoli bruciati **non servono**: il testo a frasi e' gia' sincronizzato col parlato.

## Il ritmo lo detta il parlato

Ogni evento visivo (soglie della folla, lo zero del countdown, il muro, i 22 accesi) e'
agganciato ai tempi di `words.json`, mai scelto a occhio. Il campo `parole` della spec e'
words.json **tal quale**, quarto campo compreso: e' l'indice di frase, serve al testo a schermo.

## Trappole gia' pagate (tutte viste sui fotogrammi, mai dal codice)

1. **Palette**: la v1 era navy `#0b1220`, l'errore del 28/07 ripetuto. Fondo `#16120D`, sempre.
2. **Folla come texture**: senza prospettiva (file davanti grandi e opache, dietro piccole e
   velate) 500 figure sembrano un pattern, non gente. E la folla entra **dal centro**, non da
   un bordo: "una persona sola" deve vedersi, al centro, grande.
3. **Video fermo**: quando l'azione principale finisce presto, il resto DEVE respirare
   (oscillazioni, camera che accelera, muro che vibra). Il collaudo boccia oltre 1.5s fermi —
   ha gia' bocciato il primo montaggio del reel 07 (finale immobile per 2.5s).
4. **Alpha del canvas**: un `globalAlpha` fuori da [0,1] viene IGNORATO e resta quello del
   disegno prima: il muro tornava a piena luce sotto lo slogan. Clampare sempre.
5. **UI di Instagram**: gli ultimi ~380px in basso e la colonna destra sono coperti da caption
   e icone. Niente footer: il dominio sta nella chiusura. "SALVA IL POST" e' roba da carosello,
   nei reel non esiste.

## Durata

**Sotto i 20 secondi**, misurati, non stimati: la voce con le pause di regia esce sempre piu'
lunga del previsto (il copione del 07 e' passato da 25.4 a 20.2s in tre tagli successivi).
Si taglia il copione, non si accetta il video lungo.

## Copertina

JPEG 9:16 a parte, mai un fotogramma del video. Qui il colore **puo'** stonare col dark del
feed (fondo verde pieno, testo inchiostro): serve a fermare il pollice. Restano il marchio e
il carattere. Gancio scritto, non decorativo.

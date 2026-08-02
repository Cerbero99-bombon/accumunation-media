# Registro dei cambiamenti

Ogni modifica che tocca **cosa esce, quando esce o com'e' fatto** si scrive qui prima di essere
fatta: cosa cambia, perche', che conseguenza ha, e cosa succede se va storto. Serve a Enrico per
sapere in ogni momento cosa e' stato toccato, senza doverlo chiedere.

## Finestra di silenzio
**Fra le 19:00 e le 23:00 di Roma non si tocca `queue.json`, non si toccano i trigger, non si
pusha sui media gia' in coda per stasera.** E' la finestra in cui il pubblicatore lavora: una
modifica in corsa e' il modo piu' facile per far uscire un doppione o un contenuto sbagliato.
Se una correzione e' urgente e cade dentro la finestra, si aspetta e si fa dopo, a meno che il
danno di non farla non sia peggiore: in quel caso si scrive qui perche'.

---

## 2026-08-02 (pomeriggio) · Via libera di Enrico: i reel stile D entrano in coda
**Cosa**: Enrico ha approvato il formato ("decisamente meglio. Andiamo avanti"). In coda
10 reel, due a settimana (martedì e venerdì, 20:00), dal 04/08 al 04/09:
06 stesso-prezzo · 13 countdown-che-riparte · 08 un-capo-su-cinque · 10 rispetto-a-cosa ·
09 centotrenta-chili · 11 mai-esistito · 12 ottantacinque-centesimi · 14 scarsita-funziona ·
15 uno-su-tre · 07 countdown-scaduto. Caption a canone, hashtag ruotati, cover 9:16, tutti
con collaudo + ASR PASS.
**Sostituzione**: il vecchio 03-non-e-uno-sconto (stile slideshow, superato per decisione di
Enrico del 31/07) e' USCITO dalla coda; il suo slot del 04/08 va al 06 nuovo, che copre lo
stesso tema (il meccanismo, non uno sconto). I file del 03 restano nel repo.
**Margine**: la coda passa da 4 a 33 giorni di copertura (12 contenuti futuri). Ancora sotto
i 60: tocca alla fabbrica del lunedi' colmare con caroselli e threads.
**Audio**: tutti i reel escono in modalita' autonomia (voce+musica muxata). Per l'audio in
trend serve Enrico dall'app, reel per reel: va ricordato nei report del pubblicatore.
**Rischio**: contenuti gia' approvati nel formato; il default e' approvato via
piano/da-approvare.html. Nessun trigger toccato, finestra di silenzio rispettata (15:30 Roma).
## 2026-08-02 (notte) · Il filo del cartellino, i due revisori nuovi, e i cinque della prova
**L'errore trovato da Enrico**: nel reel 11 il filo oscillava in senso opposto al cartellino.
Causa: il filo era calcolato con una formula a parte (+sin) mentre il cartellino ruota col
canvas (-sin). Classe dell'errore: un vincolo fisico ricalcolato fuori dal suo sistema di
coordinate. Regola nuova nel canone + prova delle fasi opposte su ogni aggancio.
**Revisori montati** (richiesti esplicitamente da Enrico):
- fisico-matematico: vincoli rigidi nello stesso sistema di coordinate, etichetta=scena
  (contatore 15 -> 15 figure visibili), quote esatte sparse (niente pattern i%3);
- linguistico: ASR bloccante col modello base (il tiny da' falsi positivi), blocchi >=4 parole,
  prova del senso. Scoperto e chiuso anche un buco nel MODO di chiamare il cancello: un PASS
  finto da pipe bash aveva fatto committare una voce bocciata.
**Prodotti (tutti PASS collaudo + ASR)**: 06 v2 (folla, copione nuovo con beat di senso),
08 v2 (pila, audio pulito), 09 v3 (contatore, copione con chiusura "quel costo finisce nel
prezzo"), 11 v3 (filo rigido), 15 NUOVO uno-su-tre (motivo `vetrine`, D20 Francia, R4:
30 negozi, 10 verbali contabili). Dispensa: D20 usata. Motivi nel motore: 10.
**Coda**: non toccata.
## 2026-08-02 · Rifiniture ai reel 11-12, anomalia in coda, e il circuito del riscontro
**Rifiniture (viste sui crop a piena risoluzione)**: nel 12 i titoli delle colonne restavano
in trasparenza sotto lo slogan e si incastravano col dominio; nel 11 la faccia strappata del
cartellino attraversava la riga della fonte mentre cadeva. Corretti entrambi, ri-collaudati PASS.
**Coda**: la voce non pubblicata "Reel — Non è uno sconto" (04/08) portava il permalink del
carosello G: un lettore l'avrebbe potuta credere gia' uscita. Tolto il permalink da ogni voce
con pubblicato=false. Margine coda: 3 voci future, copertura fino al 06/08 — sotto la regola
dei 60 giorni, tocca alla fabbrica del mattino.
**Circuito del riscontro (nuovo)**: attivita' settimanale `Accumunation — riscontro reel e
taratura`, trig_01D88yUi5TFhZYckqhCakfms, lunedi' 05:15 UTC (prima della fabbrica delle 06:00):
legge le insights dei contenuti pubblicati (lista chiusa di tool, solo lettura + push del
registro), aggiorna `piano/riscontri.json`, e se un motivo visivo stacca nettamente gli altri
scrive la raccomandazione nel report e UNA riga datata in fondo a `tools/CANONE-REEL.md`
sotto "## Riscontri dal pubblico". Le regole del canone si toccano coi numeri, non a sensazione.
**Nessuna pubblicazione oggi 01/08**: la coda non aveva voci per quella data (buco di ritmo
fra il 31/07 e il 02/08).
## 2026-08-01 · La revisione di Enrico sui reel 08-10, la causa vera, e i reel 11-14
**Cosa ha trovato Enrico**: (1) la pila diceva "1 su 5" e mostrava ~1 su 6, perche' i capi
distrutti sparivano dal conteggio; (2) tratti di voce storpiati ("Buttati" letto "potati",
"Mai indossata" irriconoscibile); (3) il reel 09 buttava due numeri e chiudeva senza senso;
(4) tre reel troppo simili tra loro (tutti numerone-su-fondo-scuro).
**La causa di fondo**: i cancelli controllavano la FORMA (pixel, movimento, OCR, loudness),
nessuno controllava il SIGNIFICATO: nessuno riascoltava l'audio, contava gli oggetti in
scena, o rileggeva il copione chiedendosi "e quindi?".
**Cosa e' stato montato**: `tools/asr_check.py` (riascolto bloccante di ogni blocco, gia'
attivo: ha bocciato "anti-trust" letto "antitrast" prima che finisse in un video); regola
dei blocchi >=4 parole; conto visivo sul fotogramma fermo; prova del senso sul copione;
`velo_alto:false` per i motivi a oggetto. Tutto scritto in `tools/CANONE-REEL.md`.
**Prodotti (collaudo + ASR PASS)**: 11-mai-esistito (cartellino, R5, D14) · 12-ottantacinque-
centesimi (confronto, R5, D05) · 13-countdown-che-riparte (interfaccia, R6, D11) ·
14-scarsita-funziona (domanda, R3, D19). Quattro composizioni diverse, niente numerone.
**I reel 08-10 restano fuori dalla coda**: vanno rigenerati coi cancelli nuovi dopo il
giudizio di Enrico sul formato. Il 06 (folla) ha l'audio pulito, resta valido.
**Coda**: non toccata.
## 2026-08-01 · Tre reel nuovi per la prova del formato: tre motivi, tre rubriche, tre temi
**Cosa**: Enrico ha chiesto 4-5 reel di rubriche e temi diversi per giudicare il formato
("cosa resta e cosa cambia"). Prodotti con il motore e passati dal collaudo:
- **08-un-capo-su-cinque** (19.0s) · R5 · motivo `pila` · D01+D02+D03: un capo su 5 invenduto,
  la distruzione, il divieto UE dal 19.07.2026;
- **09-centotrenta-chili** (13.0s) · R1 · motivo `contatore` · D09: 130 kg di cibo buttati a
  testa l'anno, 10 nella distribuzione (Eurostat);
- **10-rispetto-a-cosa** (18.7s) · R2 · motivo `grafico` · D15+D16: la regola del prezzo piu'
  basso dei 30 giorni, il -50% che vale 0%.
Motivi nuovi nel motore: `pila`, `contatore`, `grafico` (con `folla` e `conto` fanno cinque).
Dispensa: D01, D02, D09, D15, D16 marcate usate.
**Il collaudo ha lavorato anche stavolta**: il 10 e' stato bocciato al primo montaggio
(finale fermo 2.75s) e corretto. Difetti trovati a occhio sui provini e corretti prima del
collaudo: partenza vuota del 08, pila destra dentro la colonna delle icone IG, fantasma del
numero sotto lo slogan nel 09, picco troppo stretto e tremolio fuori tempo nel 10.
**Coda**: non toccata. I cinque esemplari (06-10) sono il campionario su cui Enrico decide.
**Rischio**: niente in pubblico.
## 2026-07-31 · Il generatore diventa pignolo: motore unico, collaudo, canone. E il primo reel non autoreferenziale
**Cosa**, in quattro pezzi:
1. **`tools/stileD/motore.py`** sostituisce `moto.py` (rimosso): scheletro condiviso per tutti i
   reel a movimento continuo + "motivi" intercambiabili (`folla`, `conto`). Un reel nuovo = un
   motivo o una spec nuova, non un renderer nuovo.
2. **`tools/collaudo.py`**: cancello automatico prima della consegna. Boccia da solo: formato,
   durata oltre i 20s, loudness fuori da -14 LUFS, video fermo oltre 1.5s, fondo navy, testo
   nelle zone coperte dalla UI di Instagram, affermazioni bandite (OCR), voce tagliata.
   Provato sul vecchio reel 03: bocciato per 4 motivi giusti. Sul 06: PASS.
3. **`tools/CANONE-REEL.md`**: cosa deve esserci in ogni reel, compresa la regola nuova sul
   contenuto: **i reel parlano al pubblico di cose vere e interessanti (dispensa), non di noi**.
   Il collegamento ad Accumunation sta nella chiusura. Richiesto da Enrico oggi.
4. **`social/reel/07-countdown-scaduto.mp4`** + cover: primo reel col motivo `conto`, dal fatto
   **D18 della dispensa** (Princeton: 393 countdown su 11.000 siti, molti validi anche da
   scaduti, 22 aziende vendono il trucco). 19.8s, PASS al collaudo, fonte a schermo.
   D18 marcata usata nella dispensa.
**Perche'**: richiesta esplicita di Enrico (31/07 sera): la qualita' deve stare nel generatore,
la sua revisione e' un plus; e i contenuti dei reel non devono essere autoreferenziali.
**Il collaudo ha gia' lavorato**: il primo montaggio del 07 e' stato BOCCIATO (2.5s fermi nel
finale) e corretto prima di arrivare a Enrico. Esattamente il compito che ha.
**Reel 06 (stesso-prezzo)**: resta nel repo come dimostrazione dello stile, contenuto giudicato
troppo banale per uscire. NON va in coda.
**Coda**: non toccata. Il 07 aspetta il via di Enrico sul primo esemplare del formato; dal
prossimo, collaudo PASS = va in coda da solo.
**Rischio se va storto**: niente in pubblico. Tutto sta nel repo.
## 2026-07-31 · Stile D rivisto (v2) e primo reel a movimento continuo finito
**Cosa**: riscritto `tools/stileD/moto.py` e prodotto `social/reel/06-stesso-prezzo-per-tutti.mp4`
(17,0 s, 1080x1920, -14 LUFS) con la sua copertina 9:16.
**Perche'**: guardando i fotogrammi della v1 sono usciti tre difetti veri, non di rifinitura:
il fondo era il navy `#0b1220` (l'errore di palette gia' pagato il 28/07, il fondo social e' il
carbone caldo `#16120D`); la folla si leggeva come una **texture** e non come gente, e lasciava
sotto il prezzo un buco nero per meta' schermo; dopo il settimo secondo il video era **fermo**,
cioe' il contrario di quello che lo stile promette.
**Cosa cambia ora**: prospettiva vera nella folla, ingresso dal centro verso i lati, prezzo che
scende addosso alla gente, respiro delle figure e camera che accelera nella seconda meta',
testo che entra a frasi con la parola pronunciata accesa, dicitura "esempio illustrativo" fissa.
**Conseguenza**: nessuna sulla coda. Il reel **non e' stato messo in `queue.json`**: siamo dentro
la finestra di silenzio e comunque manca il via libera di Enrico sullo stile.
**Rischio se va storto**: nessuno in pubblico. Il file sta nel repo e basta non metterlo in coda.
## 2026-07-31 · Correzione dei segni di pubblicazione in coda
**Cosa**: `03-g-non-e-uno-sconto` e `02-e-se-non-si-parte` erano marcati non pubblicati ma erano
gia' usciti il 30/07; `03-non-e-uno-sconto` (reel) era marcato pubblicato ma non e' mai uscito.
**Perche'**: il 30/07 il pubblicatore ha svuotato mezza coda in 35 minuti e la ricostruzione a
mano di cosa fosse uscito era stata fatta sui titoli, non sui permalink. Un reel uscito alle 23:30
era rimasto fuori dal conteggio.
**Conseguenza se non corretto**: il 2 agosto sarebbe uscito un doppione di `02-e-se-non-si-parte`,
e il reel `03-non-e-uno-sconto` non sarebbe mai uscito.
**Come e' stato verificato**: `INSTAGRAM_GET_IG_USER_MEDIA` con i permalink veri, uno per uno.
**Rischio residuo**: nessuno. I dieci media online corrispondono uno a uno alle voci marcate.

## 2026-07-31 · I reel non vanno piu' nella griglia del profilo
**Cosa**: il pubblicatore passera' `share_to_feed: false` sui reel.
**Perche'**: Enrico non vuole i reel mescolati ai post nella griglia, stonano e disordinano.
**Conseguenza**: i reel restano nella scheda Reel e nel feed degli altri, ma spariscono dalla
griglia. Non si perde distribuzione: la scheda Reel e la sezione Esplora restano identiche.
**Non retroattivo**: i due reel gia' usciti restano dove sono. Vanno tolti a mano, o rifatti.

## 2026-07-31 · Copertine dei reel con gancio
**Cosa**: ogni reel avra' un JPEG 9:16 di copertina passato come `cover_url`, con una frase gancio.
**Perche'**: i due reel usciti hanno la copertina **vuota** — il primo fotogramma e' nero perche'
il testo entra in dissolvenza. In griglia e nella scheda Reel non si capisce cosa siano.
**Conseguenza**: nessuna sul contenuto del video. Cambia solo l'anteprima.

## 2026-07-31 · Logo vecchio nei reel
**Cosa**: i tre reel erano stati renderizzati il 29/07, prima che il marchio nella skill fosse
sostituito il 30/07 alle 08:28. Portano ancora l'anello AN.
**Conseguenza**: rigenerando la spec **il logo nuovo entra da solo**, non serve toccare i sorgenti.
Il reel `03-non-e-uno-sconto`, che esce il 4 agosto, va rigenerato prima di quella data.
I due gia' usciti non si possono correggere: o restano, o si rifanno e si cancellano i vecchi.

## 2026-07-31 · I tre in evidenza corretti pubblicati in anticipo, su richiesta
**Cosa**: pin1/pin2/pin3 erano in coda per le 20:00; pubblicati a mano alle 16:59.
**Perche'**: Enrico ha chiesto di chiudere la cosa subito, i vecchi con "made in Italy" e
"non e' un algoritmo" erano ancora fissati sul profilo.
**Conseguenza**: nessuna sul calendario, erano gia' previsti per oggi. Segnati `pubblicato: true`
con i permalink veri, quindi il run delle 20:00 li salta.
**Nota tecnica**: `INSTAGRAM_CREATE_MEDIA_CONTAINER` con `child_image_urls` ora risponde 400.
Per i caroselli si usa **`INSTAGRAM_CREATE_CAROUSEL_CONTAINER`**, che accetta `child_image_urls`
direttamente. Il prompt del pubblicatore serale va aggiornato di conseguenza.

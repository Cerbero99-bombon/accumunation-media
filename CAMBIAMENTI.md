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

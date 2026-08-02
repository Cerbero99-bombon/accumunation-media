# Il canone del reel

Scritto il 31/07/2026 su richiesta esplicita di Enrico: **il generatore deve essere piu' pignolo
di lui**. La sua revisione e' un plus, non un passaggio del processo. Se Enrico trova un difetto
dopo che un reel e' passato di qui, il canone o il collaudo hanno un buco: si tappa il buco,
non solo il video.

Questo file dice **cosa deve esserci** in ogni reel. `collaudo.py` verifica la parte misurabile.
Il resto lo verifica chi produce, guardando il provino dei fotogrammi. Sempre.

---

## 1 · Contenuto: prima il pubblico, poi noi

**Un reel che parla di Accumunation e' l'eccezione, non la regola.** Il pubblico non ci conosce
e non ha motivo di interessarsi a noi: si interessa a storie vere, curiosita', trucchi svelati.
Il traffico sulla pagina arriva da li'.

- La fonte delle idee e' **`piano/dispensa.json`**: 20 fatti verificati con fonte, forza e cautele.
  Prima di inventare un tema, si guarda cosa c'e' li' dentro di `libero`.
- Gerarchia dei ganci: **sanzione vera** (AGCM, nomi e numeri) > **studio solido** (Princeton,
  Eurostat) > **legge nuova** > meccanismo nostro. L'autopromozione pura sta in fondo.
- Ogni dato detto o mostrato deve stare **gia' scritto** nella dispensa o nei documenti del
  progetto. Le cautele della voce (es. "studio del 2019, siti USA") si rispettano: la **fonte
  compare a schermo**, riga piccola, e resta finche' il dato e' in scena.
- Il collegamento ad Accumunation sta **solo nella chiusura**: slogan + dominio. Non si forza
  la morale a meta' video.
- Lo slogan e' fisso e chiude ogni reel: **"Il prezzo pieno non si augura a nessuno."** Mai
  riscritto, mai variato.

## 2 · Struttura

- **Gancio nei primi 2 fotogrammi**: si apre dentro l'azione (un countdown che corre, un numero
  che cambia), mai con una premessa o un fotogramma vuoto.
- **Movimento continuo**: una sola inquadratura che evolve, niente slideshow, niente dissolvenze
  fra schermate. Mai piu' di **1.5 secondi** percettivamente fermi (il collaudo lo misura).
- **Il ritmo lo detta il parlato**: ogni evento visivo e' agganciato a un tempo di `words.json`,
  non scelto a occhio.
- **Durata sotto i 20 secondi.** A 25 si taglia il copione, non si accetta il video lungo.
- Il testo entra **a frasi** con la parola pronunciata accesa. Mai parole sciolte, mai
  sottotitoli che ripetono cio' che e' gia' scritto grande.

## 3 · Forma

- Palette **calda** da `references/brand.md`: fondo `#16120D`, crema `#FBF8F2`, verde `#1FB877`.
  Il navy `#0b1220` e' vietato: errore gia' pagato due volte (28/07 e 31/07).
- **Zone coperte da Instagram**: niente testo essenziale negli ultimi **380px** in basso ne'
  nella colonna dei **120px** a destra fra i 900 e i 1700px di altezza (icone e caption della UI).
  Il dominio sta nella chiusura, non in un footer.
- Niente linguaggio da carosello: **"SCORRI" e "SALVA IL POST" non esistono nei reel.**
- Numeri di esempio (scala prezzi): dentro la banda R-025 (100/85/72/62) e marcati
  **"esempio illustrativo"**. I fatti veri invece portano la **fonte**, non la nota.
- Affermazioni bandite, identiche al resto della fabbrica: niente "made in Italy", niente
  "algoritmo", niente traction inventata, rimborso "garantito" mai "automatico".

## 4 · Audio

- Voce del brand: `fr-FR-RemyMultilingualNeural`, letta **frase per frase** con `vox.py`
  (ritmo, tono e pausa per frase). La frase chiave rallenta e scende; il silenzio prima del
  dato vale piu' dell'enfasi.
- Musica CC da `tools/assets/music/` (attribuzione in `LICENZE.md`), ducking sidechain,
  loudnorm a due passate → **-14 LUFS**, true peak ≤ -1.
- Scelta dichiarata nel report, reel per reel: **autonomia** (musica muxata, esce da solo) o
  **distribuzione** (solo voce, audio in trend a mano da Enrico). Non esiste una terza via.

## 5 · Consegna

Un reel e' consegnabile solo con TUTTI questi pezzi:
1. `NN-titolo.mp4` — il video, gia' **PASS al collaudo**;
2. `NN-titolo-cover.jpg` — copertina 9:16 col gancio scritto (il colore qui **puo'** stonare
   col feed, deve fermare il pollice; restano marchio e carattere del brand);
3. la **spec** e i file voce committati nel repo (senza, rifare costa dieci volte);
4. proposta di **caption** (tesi, due righe, `Link in bio.`, 🫂, 5-6 hashtag ammessi);
5. nel report: scelta audio, tema/fonte usati, esito collaudo.

## 6 · Il rito, in ordine

    dispensa → copione (max 7 frasi) → vox.py (macchina con rete) → spec → motore.py
    → shoot.py → build audio → collaudo.py → PASS? → provino GUARDATO → cover → consegna

Se il collaudo boccia, si corregge e si ripete. Se boccia tre volte per lo stesso motivo,
il difetto e' nel motore o nel canone: si corregge LI'.


---

# Aggiunta del 01/08/2026 — i tre cancelli del significato

La revisione di Enrico sui reel 08-10 ha trovato errori che i controlli di forma non vedono:
la voce che dice "potati" invece di "buttati", la pila che mostrava 1 su 6 dicendo 1 su 5,
un copione che butta due numeri e chiude senza senso. Da qui in poi:

## 1. Il cancello ASR (bloccante, automatico)
`tools/asr_check.py`, sulla macchina con rete, SUBITO dopo `vox.py`, sui singoli blocchi
`b*.wav`. Se una parola esce storpiata si riscrive il blocco, non si monta.
**Causa nota**: Remy e' una voce multilingue francese; sui blocchi corti sbaglia i fonemi.
**Regola dei blocchi: mai sotto le 4 parole.** L'effetto "parola sola" si fa con le pause.
Parole gia' bocciate: "Buttati" da solo, "Mai indossata" da sola, "anti-trust"
(dire "l'Autorità garante"). L'elisione di "a" in "augura a nessuno" e' una liaison
naturale, non un difetto.

## 2. Il conto visivo (a occhio, sul provino)
Ogni claim numerico detto o scritto va CONTATO sull'ultimo fotogramma: se dici 1 su 5,
in scena il rapporto e' 4:1, e chi sparisce deve lasciare traccia visibile (brandelli).
Un reel si guarda in pausa: il fotogramma fermo deve reggere il conteggio.

## 3. La prova del senso (prima di generare la voce)
Ogni copione, riletto da capo: problema -> fatto -> aggancio -> slogan. Se dopo l'ultimo
fatto la reazione e' "e quindi?", manca il beat di aggancio e il copione e' rotto.
Un reel non e' un elenco di numeri: e' un fatto che si chiude.

## Trappole di scena (viste sui fotogrammi, 01/08/2026)
- `velo_alto: false` nella spec per i motivi a oggetto centrale: il velo taglia l'oggetto.
- I badge (multa, sigillo) mai sotto y=1540: la UI di Instagram li copre. Si appoggiano
  SULL'oggetto (sulla card, sul cartellino), come un avviso.
- Niente elementi vivi sopra la riga della fonte (y~1506) ne' sopra il dominio in chiusura.


---

# Aggiunta del 02/08/2026 — il revisore fisico-matematico e quello linguistico

Nati dalla seconda revisione di Enrico (il filo del cartellino oscillava opposto al cartellino).

## Fisica e geometria
- **Un vincolo fisico e' UN corpo**: filo+cartellino, ombra+oggetto, contatto+appoggio si
  disegnano nello stesso sistema di coordinate (stessa rotate/translate), MAI ricalcolati con
  formule parallele. Il filo usava +sin mentre il canvas ruota a -sin: oscillavano opposti.
- **Prova delle fasi opposte**: per ogni aggancio, due fotogrammi a fasi opposte del moto,
  affiancati, e si GUARDA che il vincolo tenga da entrambe le parti.
- **Etichetta = scena**: se un contatore dice 15, le figure visibili devono essere 15. Sotto
  le ~30 unita' l'occhio conta: l'ingresso delle figure dev'essere quasi istantaneo (q/2), la
  dissolvenza lenta va bene solo oltre la soglia del contabile.
- **Le quote esatte si distribuiscono sparse**: 10 su 30 con i%3 produce due colonne perfette,
  un pattern che si vede e suona finto. Set fisso, sparso, due per riga, colonne sempre diverse.

## Lingua e audio
- Cancello ASR col modello **base** (il tiny da' falsi positivi anche sullo slogan): sui FAIL
  del tiny, ricontrollare il singolo blocco col base prima di rifare il take.
- "augura a nessuno" trascritto "augura nessuno" e' la liaison naturale di Remy, non un difetto.
- MAI validare il cancello dietro una pipe: `check | tail || ESITO=1` misura l'esito di tail.
  Il 02/08 un PASS finto ha fatto committare una voce bocciata. `set -o pipefail` o due passi.

## Audio, tetto vero
- Il loudnorm da solo non basta: l'AAC in encoding riporta il picco sopra il tetto. Catena:
  loudnorm TP=-1.5 + `alimiter=limit=0.84` sul master PCM, poi encode. Il collaudo misura il
  file FINALE decodificato, ed e' quello che conta.

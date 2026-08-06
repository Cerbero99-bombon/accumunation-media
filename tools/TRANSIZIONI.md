# Le transizioni, una per reel

Scritto il 07/08/2026. Richiesta di Enrico: «alla transizione va fatto un upgrade potente,
deve essere diverso per ogni reel, fai si' che la cosa non sia randomica e buttata li'».

La regola che ne esce: **la transizione si sceglie sul contenuto del reel, non sull'effetto.**
Se si puo' scambiare quella di un reel con quella di un altro senza che cambi niente,
e' una dissolvenza travestita e va rifatta.

| Reel | Spezzone | Transizione | Perche' proprio questa |
|---|---|---|---|
| 07-countdown-scaduto | presa che scintilla | scatto (lampo bianco + nero) | salta la corrente e il conto riparte da capo |
| 08-un-capo-su-cinque | pugno nel vetro | schegge (il fotogramma si spacca in strisce) | il capo invenduto viene distrutto |
| 09-centotrenta-chili | tanica che cade | impatto (il reel cala dall'alto) | centotrenta chili che arrivano addosso |
| 10-rispetto-a-cosa | uomo che ti convince | sterzata (panoramica con il fotogramma che scorre) | la domanda si gira dall'altra parte |
| 11-mai-esistito | animale che sbuca e sparisce | sgretola (pixelize) | un prezzo che non e' mai esistito |
| 12-ottantacinque-centesimi | versata nei bicchieri | riempi (dal basso verso l'alto) | il conto che si riempie |
| 14-scarsita-funziona | tiro e scivolata | spinta (fermo immagine + zoom in avanti) | la spinta della scarsita' finta |
| 15-uno-su-tre | giro completo sulla sbarra | giro (schiacciata verticale) | il controllo che ribalta la vetrina |
| 16-cinque-su-cento | capriola in discesa | capriola (schiacciata orizzontale) | il capitombolo del prezzo barrato |
| 17-due-posti-rimasti | salto verso la camera | addosso (cerchio che si chiude) | la pressione fabbricata che ti arriva addosso |
| 18-nel-bilancio | barca, poi piscina | stacco (nero secco) | dal bilancio alla realta', senza sfumature |
| 19-il-prezzo-in-tv | cerchio nero che vola via | cerchio (circleopen) | il cerchio in scena diventa la porta |
| 20-quattro-anni-prima | caduta per le scale | caduta (il reel scende dall'alto) | arrivare giu' quattro anni prima |
| 21-centoquarantotto | discesa sulla frana | frana (hrwind) | quasi quattrocento negozi che franano |

## Come si aggiunge un reel nuovo

`tools/motore/spezzone.py` tiene il catalogo delle transizioni con il loro perche'.
Una transizione nuova si aggiunge li' con una riga di motivazione: senza motivazione
non entra, altrimenti in tre mesi il catalogo torna a essere una lista di effetti.

## Trappola gia' pagata

Gli spezzoni di viralhooks piu' lunghi di 3 secondi contengono un fotogramma segnaposto
grigio con scritto YOUR PRODUCT SHOT, a meta' clip e non alla fine. Il 07/08 e' finito
dentro tre reel. Prima di fissare la finestra si guarda il provino del clip, sempre.

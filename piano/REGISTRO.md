# Registro: cosa vive qui, chi lo tiene in vita, quando muore

Regola di Enrico (31/07/2026): **ogni cartella e ogni file esistono per svolgere una funzione.**
Finche' quella funzione serve, dev'esserci qualcosa che lo **mantiene aggiornato in automatico**.
Quando la funzione non serve piu', il file **si chiude**: non resta li' a marcire.

Nessun file entra in `piano/` senza una riga qui dentro. Se una riga ha `manutentore: nessuno`,
o quel file trova un manutentore, o va archiviato.

| File | A cosa serve | Chi lo tiene aggiornato | Quando muore |
|---|---|---|---|
| `temi.json` + `temi.py` | i 100 temi dei post e il loro stato | il programmatore, a ogni produzione, con `temi.py usa` | quando i temi liberi finiscono: allora si rifa' la lista dei vantaggi e la griglia si rigenera |
| `griglia-contenuti.html` | vedere a colpo d'occhio cosa e' gia' stato usato | si rigenera da `temi.json`, mai a mano | insieme a `temi.json` |
| `reel.json` + `reel.py` | le 272 combinazioni dei reel | il programmatore, con `reel.py usa` | quando cambiano le rubriche o i problemi: si rigenera |
| `griglia-reel.html` | stessa cosa, per i reel | si rigenera da `reel.json` | insieme a `reel.json` |
| `dispensa.json` + `dispensa.py` | fonti vere da citare nei contenuti | **attivita' mensile di rifornimento** (da creare) + chi produce, che marca le voci usate | mai: finche' pubblichiamo serve materiale. Ma le voci **scadono**: un dato di 3 anni fa va ricontrollato |
| `dispensa.html` | consultare le fonti e le cautele | si rigenera da `dispensa.json` | insieme a `dispensa.json` |
| `idee.json` + `idee.py` | le idee di Enrico e le cose in mano a lui | attivita' `plancia`, ogni venerdi' | mai: e' l'archivio della testa di Enrico |
| `plancia.html` | quello che Enrico deve guardare | si rigenera da `idee.json` | insieme a `idee.json` |
| `approva.py` → `da-approvare.html` | approvare i contenuti prima che escano | si rigenera a ogni pubblicazione e a ogni produzione | quando Enrico smettera' di voler approvare in anticipo |
| `raw.json` | la griglia originale da cui e' nato `temi.json` | nessuno: e' un sorgente storico | **archiviabile**: serve solo se si rifa' l'init da zero |
| `../queue.json` | cosa esce e quando | pubblicatore serale + programmatore | mai |
| `../CAMBIAMENTI.md` | cosa e' stato toccato e con che conseguenza | chiunque tocchi pubblicazione o contenuti, **prima** di toccarli | mai |
| `../tools/` | pipeline audio e montaggio dei reel | chi produce reel; da rivedere se cambia lo stile | quando cambia la pipeline |

## Come si aggiunge una riga

Un file nuovo in `piano/` senza riga in questa tabella e' un errore: si scrive prima la riga,
poi si crea il file. Le tre domande, sempre le stesse:
1. **a cosa serve**, in una frase che non sia il nome del file;
2. **chi lo tiene aggiornato**, con il nome dell'attivita' o del ruolo, non "si aggiorna da solo";
3. **quando muore**, cioe' la condizione che lo rende inutile. Se non esiste, si scrive "mai" e si
   spiega perche'.

## Manutenzione del registro stesso

Lo controlla l'attivita' **plancia**, ogni venerdi': verifica che ogni file presente abbia una riga,
che ogni riga abbia un file, e che nessun manutentore sia "nessuno". Quello che non torna finisce
nel messaggio a Enrico, non in un log che non legge nessuno.

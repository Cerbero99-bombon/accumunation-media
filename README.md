# Media Accumunation

Immagini e video dei contenuti social, ospitati qui solo per essere serviti su URL pubblico
diretto: l'API di Meta va a prendersi i file da sé e non accetta link con parametri.

Non è il sito. Il sito è accumunation.it.

## Canale Threads

Threads è un canale della coda come Instagram: le uscite stanno in `queue.json` con
`"tipo": "threads"` e il testo nel campo `testo` (in mancanza si usa `caption`, poi `titolo`).
Il testo è l'unica cosa che esce: post di solo testo, niente media, massimo 500 caratteri.

Le pubblica `tools/pubblica_threads.py`. Due passi dell'API di Meta: prima si crea il
contenitore (`POST /me/threads`, `media_type=TEXT`), poi lo si pubblica
(`POST /me/threads_publish`, `creation_id=...`); il permalink si legge subito dopo e finisce
nella voce insieme a `pubblicato: true`. Una voce non pubblicata non porta mai il `permalink`.

**Il dry-run è il default.** Senza `--vai` il programma non tocca la rete e non scrive nulla:

    python3 tools/pubblica_threads.py            # dal container: solo dry-run

**Dal container non si pubblica**: verso `graph.threads.net` non c'è rete. La pubblicazione
vera gira su una macchina con rete (`COMPOSIO_REMOTE_BASH_TOOL`), che scarica coda e script da
raw.githubusercontent, pubblica, e restituisce la coda aggiornata da ricommittare qui.
La procedura esatta, tre comandi, sta nel commento in cima a `tools/pubblica_threads.py`.

Vale anche qui la finestra di silenzio 19:00–23:00 Roma di `CAMBIAMENTI.md`.

### Il token scade

`THREADS_TOKEN` (in `.cerbero-secrets` sul computer di Enrico, insieme a `THREADS_USER_ID`)
**scade il 29/09/2026**. Il rinnovo è già schedulato per il **15/09/2026**, due settimane
prima, così un rinnovo mancato si può ancora recuperare a mano. Token scaduto = ogni run
fallisce in creazione del contenitore, quindi nessuna voce viene marcata `pubblicato` e
niente va perso: alla ripresa esce tutto l'arretrato (fino a 3 per run).

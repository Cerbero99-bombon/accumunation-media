# Pipeline audio dei Reel

Verificata end-to-end il 31/07/2026: un reel da 30 secondi si monta in **22 secondi**,
esce 1080x1920 h264 30fps, AAC 48kHz, **-14.0 LUFS** e true peak -0.9 dBFS (lo standard dei social).

## Due fasi, perche' la rete e' divisa in due

**Fase 1 — su una macchina con Internet** (`COMPOSIO_REMOTE_BASH_TOOL`). Dal container gli
endpoint Microsoft e HuggingFace sono bloccati, quindi la voce si genera fuori.

    pip install edge-tts
    python3 tools/tts_edge.py "testo del reel" voce.mp3 words.json
    ffmpeg -y -i voce.mp3 -ar 48000 -ac 1 voce.wav

`words.json` contiene i tempi **parola per parola** che il motore restituisce gratis.
Questo e' il punto chiave: siccome la voce la scriviamo noi, i sottotitoli sono esatti
senza trascrizione. Niente whisper, niente allineamento forzato, zero errori
(whisper scriveva "90%" dove il copione diceva "novanta per cento").

**Fase 2 — nel container**, tutto il resto:

    pip install librosa
    ./tools/build_reel.sh voce.wav musica.m4a words.json frames/ FINAL.mp4

`build_reel.sh` fa: griglia dei beat con librosa, tagli visivi ogni 4 beat, video muto h264,
ducking sidechain, loudnorm a due passate, sottotitoli karaoke bruciati, mux finale.

## Tarature misurate, non stimate

- **Ducking**: `sidechaincompress=threshold=0.05:ratio=6:attack=10:release=350` → la musica
  scende di 11.2 dB sotto la voce e resta intatta nei silenzi. A `threshold=0.02:ratio=12`
  sparisce (19.4 dB), a `0.15:ratio=3` non si sente (3.5 dB).
- **Voce**: `acompressor=threshold=0.125:ratio=3:makeup=2`. Il `makeup` e' obbligatorio:
  senza, ffmpeg abbassa la voce di 11 dB e diventa inudibile nel mix.
- **amix**: serve `normalize=0`, altrimenti i livelli vengono dimezzati.
- **loudnorm**: due passate. Con una sola si finisce 2.4 dB sotto il bersaglio.

## Cosa non funziona qui, e perche'

| Cosa | Perche' |
|---|---|
| `edge-tts` dal container | endpoint Microsoft irraggiungibile |
| `piper.download_voices`, `faster-whisper` dal container | i modelli stanno su huggingface.co, bloccato |
| `pip install aubio` | nessuna wheel per Python 3.11. Usare librosa |
| coqui XTTS | serve torch e ~4 GB di RAM. Non testato |
| clonazione della voce di Enrico | serve una macchina con GPU. Non e' un muro, e' lavoro |

## Musica

Niente tracce protette: si costruisce una libreria libera in `music/`, formato **AAC 128k
48 kHz .m4a**, tagli da 30-40 secondi, circa 600 KB l'uno. Fonte verificata raggiungibile:
incompetech.com (Kevin MacLeod, CC-BY, **l'attribuzione e' obbligatoria** e va scritta in
`music/LICENZE.md`). GitHub regge fino a 100 MB per file; niente Git LFS, perche' i file LFS
non vengono serviti come binari da raw.githubusercontent.com.

## Il limite che decide la strategia, reel per reel

Muxare una traccia dentro l'MP4 **non e'** taggare l'audio in trend di Instagram. Il reel non
compare nella pagina di quel suono, nessuno puo' riusarlo, l'algoritmo non lo associa al trend.
Quindi ogni reel e' una scelta:

- **autonomia**: voce del brand + musica libera muxata. Esce da solo, look coerente, zero lavoro manuale.
- **distribuzione**: video con la sola voce (o musica bassissima), audio in trend messo a mano
  dall'app al momento del post. Costa un passaggio umano, compra la spinta del suono.

Non esiste una terza via: chi dice il contrario non ha provato.

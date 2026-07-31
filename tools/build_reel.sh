#!/usr/bin/env bash
# build_reel.sh VOCE.wav MUSICA.wav WORDS.json FRAMES_DIR OUT.mp4
set -euo pipefail
VOICE="$1"; MUSIC="$2"; WORDS="$3"; FRAMES="$4"; OUT="$5"
W=1080; H=1920; FPS=30; T=${T:-30}

# 1) griglia dei beat
python3 - "$MUSIC" > beats.json <<'PY'
import sys,json,librosa,numpy as np
y,sr=librosa.load(sys.argv[1],sr=22050,mono=True)
_,b=librosa.beat.beat_track(y=y,sr=sr,units='time')
json.dump([round(float(x),3) for x in b],sys.stdout)
PY

# 2) lista slide tagliate ogni 4 beat
python3 - "$FRAMES" "$T" > slides.txt <<'PY'
import sys,json,glob,os
frames=sorted(glob.glob(os.path.join(sys.argv[1],"*.png"))); T=float(sys.argv[2])
beats=json.load(open("beats.json")); cuts=[b for i,b in enumerate(beats) if i%4==0 and b<T]+[T]
out=[]
for i in range(len(cuts)-1):
    out.append("file '%s'\nduration %.3f"%(frames[i%len(frames)],cuts[i+1]-cuts[i]))
out.append("file '%s'"%frames[(len(cuts)-2)%len(frames)])
print("\n".join(out))
PY

# 3) video muto sui tagli
ffmpeg -y -v error -f concat -safe 0 -i slides.txt \
  -vf "scale=$W:$H:force_original_aspect_ratio=decrease,pad=$W:$H:(ow-iw)/2:(oh-ih)/2,fps=$FPS,format=yuv420p" \
  -an -c:v libx264 -preset medium -crf 20 -t $T video_mute.mp4

# 4) voce + musica con ducking
ffmpeg -y -v error -i "$MUSIC" -i "$VOICE" -filter_complex "\
[1:a]highpass=f=80,acompressor=threshold=0.125:ratio=3:attack=10:release=200:makeup=2[voc];\
[voc]asplit=2[vo][key];\
[0:a]volume=-6dB,afade=t=out:st=$(python3 -c "print($T-1.5)"):d=1.5[mus];\
[mus][key]sidechaincompress=threshold=0.05:ratio=6:attack=10:release=350[duck];\
[duck][vo]amix=inputs=2:duration=longest:normalize=0[mix]" \
  -map "[mix]" -ar 48000 -ac 2 -t $T premaster.wav

# 5) loudnorm a due passate -> -14 LUFS
ffmpeg -hide_banner -nostats -i premaster.wav -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json \
  -f null - 2>&1 | sed -n '/^{/,/^}/p' > ln.json
read MI MTP MLRA MTH MOFF < <(python3 -c "
import json;d=json.load(open('ln.json'))
print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
ffmpeg -y -v error -i premaster.wav -af \
 "loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=$MI:measured_TP=$MTP:measured_LRA=$MLRA:measured_thresh=$MTH:offset=$MOFF:linear=true" \
 -ar 48000 -ac 2 master.wav

# 6) sottotitoli parola-per-parola + mux finale
python3 mk_ass.py "$WORDS" subs.ass >/dev/null
ffmpeg -y -v error -i video_mute.mp4 -i master.wav -vf "ass=subs.ass" \
  -c:v libx264 -preset medium -crf 20 -profile:v high -level 4.0 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart "$OUT"
echo "OK -> $OUT"

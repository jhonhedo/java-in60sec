#!/usr/bin/env bash
# Render + mix one episode.
# Usage: ./make_episode.sh <module> <duration_seconds> <voice.mp3> <output.mp4>
# Example: ./make_episode.sh hm 53 hashmap_om.mp3 java_hashmap_om.mp4
set -euo pipefail
MOD=$1; DUR=$2; VO=$3; OUT=$4
HALF=$(python3 -c "print($DUR/2)")
ANIM=$MOD python3 render.py 0 "$HALF" part1.mp4 &
ANIM=$MOD python3 render.py "$HALF" "$DUR" part2.mp4 &
ANIM=$MOD OUT=sfx_$MOD.wav python3 sound.py &
wait
printf "file 'part1.mp4'\nfile 'part2.mp4'\n" > parts.txt
ffmpeg -v error -y -f concat -safe 0 -i parts.txt -c copy video_only.mp4
ffmpeg -v error -y -i video_only.mp4 -i "$VO" -i "sfx_$MOD.wav" -filter_complex \
 "[1:a]aresample=48000,highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo,asplit=2[vo][sc];[2:a][sc]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=250[duck];[duck][vo]amix=inputs=2:normalize=0,alimiter=limit=0.93[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t "$DUR" -movflags +faststart "$OUT"
rm -f part1.mp4 part2.mp4 parts.txt video_only.mp4
echo "done: $OUT"

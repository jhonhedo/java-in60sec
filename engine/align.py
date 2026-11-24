"""Word-level forced alignment of a voiceover against its script.
Usage: python3 align.py voice.mp3 script.txt
Prints word@seconds for every word; use these to write the WARP anchors (anim_time, audio_time).
Needs: pip install pocketsphinx ; ffmpeg on PATH.
"""
import sys, re, subprocess
from pocketsphinx import Decoder

EXTRA = {  # pronunciations for words missing from the CMU dictionary
    'arraylist': 'ER EY L IH S T', 'linkedlist': 'L IH NG K T L IH S T', 'hashmap': 'HH AE SH M AE P',
    'hashcode': 'HH AE SH K OW D', 'thats': 'DH AE T S', 'lets': 'L EH T S', 'rehashes': 'R IY HH AE SH IH Z',
    'reuses': 'R IY Y UW Z IH Z', 'relink': 'R IY L IH NG K', 'cpu': 'S IY P IY Y UW', 'jvm': 'JH EY V IY EH M',
}

mp3, script = sys.argv[1], sys.argv[2]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                     capture_output=True, check=True).stdout
words = re.sub(r"[^a-z0-9 ]", " ", open(script).read().lower().replace("'", "")).split()
d = Decoder(samprate=16000, loglevel='ERROR', bestpath=False)
for w in sorted(set(words)):
    if d.lookup_word(w) is None:
        if w not in EXTRA: sys.exit(f'Unknown word "{w}": add its phonemes to EXTRA')
        d.add_word(w, EXTRA[w], False)
d.set_align_text(' '.join(words))
d.start_utt(); d.process_raw(raw, full_utt=True); d.end_utt()
segs = [(s.word, s.start_frame / 100) for s in d.seg() if s.word not in ('<s>', '</s>', '<sil>')]
print(f'{len(segs)}/{len(words)} words aligned')
print(' '.join(f'{w}@{a:.2f}' for w, a in segs))

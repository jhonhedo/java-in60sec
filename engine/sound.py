import numpy as np, wave, random
import importlib, os
anim = importlib.import_module(os.environ.get("ANIM", "anim"))

SR = 48000
N = int(anim.DUR * SR)
rng = np.random.default_rng(7)
out = np.zeros((N, 2))

def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)

def lp(x, k):  # one-pole lowpass
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y

def tone(freqs, dur, a, d, vol):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) / (j + 1) for j, f in enumerate(freqs))
    return s * env(n, a, d) * vol

def sweep(f0, f1, dur, d, vol):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.geomspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.003, d) * vol

def noise(dur, k, a, d, vol):
    n = int(dur * SR); return lp(rng.standard_normal(n), k) * env(n, a, d) * vol

CACHE = {}
def mix(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o
def make(kind):
    if kind == 'key':
        n = noise(0.035, 0.5, 0.001, 0.008, 0.25)
        return mix(n, tone([random.uniform(1800, 2600)], 0.03, 0.001, 0.006, 0.05))
    if kind == 'pop': return sweep(260, 760, 0.16, 0.05, 0.45)
    if kind == 'pop2': return mix(sweep(200, 520, 0.22, 0.07, 0.5), tone([1040], 0.25, 0.002, 0.06, 0.08))
    if kind == 'tick': return tone([2400, 3600], 0.08, 0.001, 0.015, 0.22)
    if kind == 'blip': return tone([1320, 2640], 0.18, 0.002, 0.05, 0.28)
    if kind == 'whoosh':
        n = int(0.5 * SR); t = np.arange(n) / SR
        e = np.sin(np.pi * t / 0.5) ** 2
        return lp(rng.standard_normal(n), 0.06) * e * 0.9
    if kind == 'ding': return tone([880, 1318.5, 1760], 1.2, 0.003, 0.35, 0.32)
    if kind == 'buzz':
        n = int(0.32 * SR); t = np.arange(n) / SR
        s = np.sign(np.sin(2 * np.pi * 98 * t)) * 0.5 + np.sin(2 * np.pi * 147 * t) * 0.5
        return lp(s, 0.15) * env(n, 0.005, 0.12) * 0.42
    if kind == 'boom': return mix(sweep(120, 40, 0.9, 0.3, 0.8), noise(0.4, 0.1, 0.002, 0.08, 0.4))
    if kind == 'scan': return sweep(400, 1600, 1.1, 0.9, 0.12)
    if kind == 'found': return tone([1046.5, 1568], 0.6, 0.003, 0.18, 0.3)
    if kind == 'down': return sweep(500, 140, 0.6, 0.3, 0.25)
    if kind == 'swell':
        n = int(1.6 * SR); t = np.arange(n) / SR
        e = (t / 1.6) ** 2 * np.exp(-np.maximum(t - 1.3, 0) * 20)
        return lp(rng.standard_normal(n), 0.03) * e * 0.9
    raise KeyError(kind)

for t, kind in anim.SFX:
    t = anim.to_audio(t)
    s = make(kind); i = int(t * SR); j = min(N, i + len(s))
    pan = 0.5 if kind != 'key' else random.uniform(0.4, 0.6)
    out[i:j, 0] += s[:j - i] * (1 - pan) * 2 * 0.5
    out[i:j, 1] += s[:j - i] * pan * 2 * 0.5

# ambient pad: Am - F - C - G, 6s each
t = np.arange(N) / SR
chords = [[110, 164.8, 220, 261.6], [87.3, 130.8, 174.6, 220], [130.8, 196, 261.6, 329.6], [98, 146.8, 196, 246.9]]
pad = np.zeros(N)
for k, ch in enumerate(chords * 3):
    st = k * 5.0; n0, n1 = int(st * SR), min(N, int((st + 6.0) * SR))
    if n0 >= N: break
    tt = t[n0:n1] - st
    e = np.minimum(tt / 1.2, 1) * np.minimum((6.0 - tt) / 1.2, 1)
    seg = sum(np.sin(2 * np.pi * f * tt * (1 + d)) for f in ch for d in (-0.002, 0.002))
    pad[n0:n1] += seg * e
pad = pad / np.abs(pad).max() * 0.07 * (1 + 0.15 * np.sin(2 * np.pi * 0.2 * t))
# subtle pulse beat (soft kick) from 9s to 42s at 100 bpm
for bt in np.arange(*getattr(anim, "BEAT", (5.7, 41.4)), 0.6):
    s = sweep(110, 45, 0.25, 0.08, 0.22); i = int(bt * SR); out[i:i + len(s)] += s[:, None]
out += pad[:, None]
fade = np.minimum(1, np.minimum(t / 0.3, (anim.DUR - t) / 1.5))[:, None]
out *= fade
out = np.tanh(out * 1.4) / np.tanh(1.4)
out = out / np.abs(out).max() * 0.89 * 0.32
with wave.open(os.environ.get('OUT', 'sfx.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())
print('ok', len(anim.SFX), 'events')

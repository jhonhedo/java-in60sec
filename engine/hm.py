import math, random, numpy as np, skia
from anim import (W, H, FPS, F, hexc, P, rrect, text, tokens_draw, eio, eout, eback, prog, lerp, cl, arrow, glowblob,
                  BG, VIG, MONO_B, MONO_R, INTER_BLK, INTER_B, INTER_SB, STACK, POOL, HEAP, TRUEC, FALSEC, TXT, MUTED,
                  PANEL, KW, KW2, STR, OP, PUN, ID, FN)
NUM = '#F78C6C'
DUR = 53.0

def jhash(s):
    h = 0
    for ch in s: h = (31 * h + ord(ch)) & 0xFFFFFFFF
    return h
def signed(h): return h - (1 << 32) if h >= 1 << 31 else h
def spread(h): return h ^ (h >> 16)
KEYS = {'apple': 1, 'mango': 2, 'kiwi': 3, 'lemon': 4}
INFO = {k: (signed(jhash(k)), spread(jhash(k)), spread(jhash(k)) & 15) for k in KEYS}
assert [INFO[k][2] for k in KEYS] == [1, 15, 2, 2]

# ---------------- timeline (animation time) ----------------
T = dict(hk=(0.3, 1.4), hk_n=1.7, hk_r=2.4, how=3.2, hout=(4.0, 4.6),
         lay=(4.6, 7.0),
         L=[(7.2, 8.4), (11.6, 12.4), (14.4, 15.1), (17.2, 18.0), (23.0, 23.9)],
         P=[(8.5, 1.0), (12.5, 0.6), (15.2, 0.6), (18.1, 1.0), (24.0, 0.6)],
         dim=25.3, cur=25.5, x1=26.0, mv=26.6, ok=27.0, val=(27.4, 27.9), o1=28.2,
         tree=(30.0, 34.5), grow=(30.4, 31.6), morph=(31.8, 32.8), tlab=33.0,
         rs=(34.6, 39.6), load=(35.0, 36.2), dbl=(36.5, 37.5), rh=(37.7, 38.6),
         end=(40.0, 40.8))
ORDER = ['apple', 'mango', 'kiwi', 'lemon', 'lemon']
# pipeline phase offsets at speed 1.0
PH = dict(key=0.0, hc=0.3, hc_done=0.8, bits=1.0, bits_done=1.4, mask=1.5, idx=1.8, fly=2.2, land=2.8)
def ph(i, name): s, sp = T['P'][i]; return s + PH[name] * sp

CODE = [
    [('map', ID), ('.put', FN), ('(', PUN), ('"apple"', STR), (', ', PUN), ('1', NUM), (');', PUN)],
    [('map', ID), ('.put', FN), ('(', PUN), ('"mango"', STR), (', ', PUN), ('2', NUM), (');', PUN)],
    [('map', ID), ('.put', FN), ('(', PUN), ('"kiwi"', STR), (', ', PUN), ('3', NUM), (');', PUN)],
    [('map', ID), ('.put', FN), ('(', PUN), ('"lemon"', STR), (', ', PUN), ('4', NUM), (');', PUN)],
    [('map', ID), ('.get', FN), ('(', PUN), ('"lemon"', STR), (');', PUN), ('  // returns 4', MUTED)],
]
HOOK = [('map', ID), ('.get', FN), ('(', PUN), ('"lemon"', STR), (')', PUN)]
def txt(t_): return ''.join(s for s, _ in t_)

CAPS = [
    (0.0, 4.4, [('How does HashMap find it ', TXT), ('instantly?', STACK)]),
    (4.8, 7.1, [('Just an array of ', TXT), ('16 buckets', POOL)]),
    (7.2, 11.5, [('hashCode()', FN), (' → mix bits → ', TXT), ('& 15', POOL)]),
    (11.6, 17.1, [('Every key jumps to ', TXT), ('its bucket', POOL)]),
    (17.2, 22.8, [('Same bucket? ', TXT), ('Collision', FALSEC), (' → chain it', TXT)]),
    (23.0, 29.8, [('Jump to bucket, then ', TXT), ('equals()', TRUEC)]),
    (30.0, 34.5, [('8+ in one bucket → ', TXT), ('tree', FALSEC)]),
    (34.6, 39.8, [('75% full → ', TXT), ('double & rehash', HEAP)]),
]

# ---------------- SFX list ----------------
SFX = []
def type_ev(rng, s):
    for i, ch in enumerate(s):
        if ch != ' ': SFX.append((rng[0] + (i + 1) / len(s) * (rng[1] - rng[0]), 'key'))
type_ev(T['hk'], txt(HOOK))
for toks, rng in zip(CODE, T['L']): type_ev(rng, txt(toks[:5]) if toks[-1][1] == MUTED else txt(toks))
SFX += [(T['hk_n'], 'tick'), (T['hk_r'], 'ding'), (T['how'], 'boom'), (T['hout'][0], 'whoosh'), (T['lay'][0], 'swell')]
for k in range(16): SFX.append((5.2 + k * 0.09, 'key'))
for i in range(5):
    SFX += [(ph(i, 'key'), 'pop'), (ph(i, 'hc'), 'scan'), (ph(i, 'mask'), 'tick'), (ph(i, 'idx'), 'pop2')]
    if i < 4: SFX += [(ph(i, 'fly'), 'whoosh'), (ph(i, 'land'), 'found' if i != 3 else 'buzz')]
SFX += [(ph(3, 'land') + 0.45, 'pop'), (T['dim'], 'down'), (T['cur'], 'tick'), (T['x1'], 'buzz'), (T['mv'], 'whoosh'),
        (T['ok'], 'ding'), (T['val'][0], 'pop2'), (T['o1'], 'boom'), (T['tree'][0], 'swell'), (T['morph'][0], 'scan'),
        (T['tlab'], 'found'), (T['rs'][0], 'swell'), (T['dbl'][0], 'boom'), (T['rh'][0], 'scan'), (T['end'][0], 'swell')]
SFX += [(lerp(*T['grow'], i / 7), 'blip') for i in range(8)]
SFX += [(lerp(*T['load'], i / 11), 'key') for i in range(12)]

# ---------------- geometry ----------------
ROW_Y0, ROW_P = 912, 49
def row_y(i): return ROW_Y0 + i * ROW_P
NODE_W, NODE_H = 214, 38
def slot_x(k): return 158 + k * 262
PIPE = (50, 668, 1030, 872)

def node(c, key, x, y, a=1.0, s=1.0, col=POOL, glow=0.0, val=None):
    if a <= 0.01: return
    cx, cy = x + NODE_W / 2, y + NODE_H / 2
    c.save(); c.translate(cx, cy); c.scale(s, s); c.translate(-cx, -cy)
    if glow > 0: rrect(c, x - 6, y - 6, x + NODE_W + 6, y + NODE_H + 6, 14, P(col, 0.7 * glow * a, blur=12))
    rrect(c, x, y, x + NODE_W, y + NODE_H, 10, P('#0B1424', 0.96 * a))
    rrect(c, x, y, x + NODE_W, y + NODE_H, 10, P(col, 0.85 * a, stroke=2))
    text(c, f'"{key}"', x + 14, y + 27, F(MONO_B, 24), STR, a)
    text(c, str(KEYS[key] if val is None else val), x + NODE_W - 16, y + 27, F(MONO_B, 24), NUM, a, 'r')
    c.drawLine(x + NODE_W - 46, y + 8, x + NODE_W - 46, y + NODE_H - 8, P(MUTED, 0.6 * a, stroke=2))
    c.restore()

def verdict(c, cx, cy, ok, k):
    if k <= 0: return
    col = TRUEC if ok else FALSEC
    c.save(); c.translate(cx, cy); c.scale(k, k)
    rrect(c, -118, -26, 118, 26, 26, P('#0A0F1C', .95)); rrect(c, -118, -26, 118, 26, 26, P(col, 1, stroke=2))
    text(c, 'equals()', -14, 9, F(MONO_B, 26), col, 1, 'c')
    ix = 84; c.drawCircle(ix, 0, 15, P(col, 1))
    pth = skia.Path()
    if ok: pth.moveTo(ix - 7, 0); pth.lineTo(ix - 2, 6); pth.lineTo(ix + 8, -6)
    else: pth.moveTo(ix - 6, -6); pth.lineTo(ix + 6, 6); pth.moveTo(ix + 6, -6); pth.lineTo(ix - 6, 6)
    c.drawPath(pth, P('#0A0F1C', 1, stroke=4))
    c.drawLine(0, -26, 0, -26, P(col)); c.restore()

def bits_str(v): b = format(v, '032b'); return ' '.join(b[i:i + 4] for i in range(0, 32, 4))

def card(c, a, k):
    c.drawRect(skia.Rect.MakeLTRB(0, 650, W, 1730), P('#050812', 0.78 * a))
    cx, cy = W / 2, 1260
    c.save(); c.translate(cx, cy); s = 0.85 + 0.15 * k; c.scale(s, s); c.translate(-cx, -cy)
    rrect(c, 90, 760, 990, 1700, 34, P('#0C1426', 0.97 * a)); rrect(c, 90, 760, 990, 1700, 34, P('#33416A', a, stroke=2))
    c.restore()

# ---------------- frame ----------------
def draw(c, t, real):
    c.drawImage(BG, 0, -(t * 1.6) % 40)
    glowblob(c, 160 + 60 * math.sin(t * 0.3), 420, 520, POOL, 0.10)
    glowblob(c, 930 + 50 * math.cos(t * 0.25), 1400, 600, HEAP, 0.10)

    # ===== HOOK =====
    ho = 1 - eio(prog(t, *T['hout']))
    if ho > 0:
        c.save(); sc = 1 + 0.08 * (1 - ho); c.translate(W / 2, H / 2); c.scale(sc, sc); c.translate(-W / 2, -H / 2)
        a = ho
        text(c, 'JAVA  •  60 SECONDS', W / 2, 330, F(INTER_B, 30), POOL, a * eout(prog(t, 0, .5)), 'c')
        fm = F(MONO_B, 74); s_ = txt(HOOK); n = int(len(s_) * prog(t, *T['hk']) + 1e-6)
        x = tokens_draw(c, HOOK, n, W / 2 - fm.measureText(s_) / 2, 700, fm, a)
        if n < len(s_) and int(t * 4) % 2 == 0: rrect(c, x + 3, 640, x + 10, 712, 2, P(TXT, a))
        if t > T['hk_n']:
            k = eout(prog(t, T['hk_n'], T['hk_n'] + .4))
            cnt = int(1_000_000 * eout(prog(t, T['hk_n'], T['hk_n'] + .6)))
            text(c, f'{cnt:,} entries', W / 2, 840 + 20 * (1 - k), F(INTER_B, 52), MUTED, a * k, 'c')
        if t > T['hk_r']:
            k = eback(prog(t, T['hk_r'], T['hk_r'] + .35))
            c.save(); c.translate(W / 2, 990); c.scale(k, k)
            lab = 'found in 1 jump'; fw = F(MONO_B, 50).measureText(lab) + 70
            rrect(c, -fw / 2, -48, fw / 2, 32, 40, P(TRUEC, .18 * a)); rrect(c, -fw / 2, -48, fw / 2, 32, 40, P(TRUEC, a, stroke=3))
            text(c, lab, 0, 9, F(MONO_B, 50), TRUEC, a, 'c', glow=10); c.restore()
        if t > T['how']:
            k = eback(prog(t, T['how'], T['how'] + .4), 2.6)
            c.save(); c.translate(W / 2, 1360); c.scale(k, k)
            text(c, 'HOW?', 0, 0, F(INTER_BLK, 230), STACK, a, 'c', glow=30); c.restore()
        c.restore()

    endk = eio(prog(t, *T['end']))
    if t >= T['lay'][0]:
        # header
        ha = eout(prog(t, T['lay'][0], T['lay'][0] + .6))
        c.save(); c.translate(0, -30 * (1 - ha))
        tag = 'JAVA IN 60s'; fw = F(INTER_B, 26).measureText(tag) + 40
        rrect(c, 60, 72, 60 + fw, 116, 22, P(POOL, .15 * ha)); rrect(c, 60, 72, 60 + fw, 116, 22, P(POOL, .8 * ha, stroke=2))
        text(c, tag, 80, 103, F(INTER_B, 26), POOL, ha)
        x = 60 + text(c, 'HashMap', 60, 196, F(MONO_B, 64), FN, ha)
        text(c, '  internals', x, 196, F(INTER_B, 46), MUTED, ha)
        c.restore()

        # code panel
        ca = eout(prog(t, T['lay'][0] + .2, T['lay'][0] + .9))
        c.save(); c.translate(0, 40 * (1 - ca))
        rrect(c, 50, 232, 1030, 636, 28, P(PANEL, .92 * ca)); rrect(c, 50, 232, 1030, 636, 28, P('#2A3654', ca, stroke=2))
        for i, col in enumerate(['#FF5F57', '#FEBC2E', '#28C840']): c.drawCircle(88 + i * 30, 268, 9, P(col, ca))
        text(c, 'Main.java', 540, 277, F(INTER_SB, 24), MUTED, ca, 'c')
        fm = F(MONO_B, 35); active = max([i for i, r in enumerate(T['L']) if t >= r[0] - .15] or [-1])
        for i, (toks, rng) in enumerate(zip(CODE, T['L'])):
            y = 342 + i * 62
            if i == active:
                hk = eout(prog(t, rng[0] - .15, rng[0] + .15))
                rrect(c, 62, y - 42, 1018, y + 18, 12, P('#1C2847', .9 * hk * ca)); rrect(c, 62, y - 42, 68, y + 18, 3, P(POOL, hk * ca))
            text(c, str(i + 1), 104, y, F(MONO_R, 28), MUTED, ca * (1 if t >= rng[0] else .35), 'r')
            if t >= rng[0]:
                body = toks[:-1] if toks[-1][1] == MUTED else toks
                s_ = txt(body); n = int(len(s_) * prog(t, *rng) + 1e-6)
                x = tokens_draw(c, body, n, 135, y, fm, ca)
                if body is not toks and t > T['val'][1]:
                    text(c, toks[-1][0], x, y, fm, TRUEC, ca * eout(prog(t, T['val'][1], T['val'][1] + .4)))
                if i == active and (n < len(s_) or int(t * 2.2) % 2 == 0) and t < T['end'][0]:
                    rrect(c, x + 3, y - 32, x + 7, y + 8, 2, P(POOL, ca))
        c.restore()

        # pipeline panel
        pa = eout(prog(t, T['lay'][0] + .5, T['lay'][0] + 1.2))
        l, tp, r, b = PIPE
        rrect(c, l, tp, r, b, 24, P('#0A1222', .9 * pa)); rrect(c, l, tp, r, b, 24, P(FN, .55 * pa, stroke=2))
        fw = F(INTER_BLK, 22).measureText('HASH()') + 30
        rrect(c, l + 20, tp - 18, l + 20 + fw, tp + 18, 18, P('#1F1A05', pa)); rrect(c, l + 20, tp - 18, l + 20 + fw, tp + 18, 18, P(FN, pa, stroke=2))
        text(c, 'HASH()', l + 35, tp + 8, F(INTER_BLK, 22), FN, pa)
        cur = max([i for i in range(5) if t >= T['P'][i][0]] or [-1])
        if cur >= 0:
            key = ORDER[cur]; hc, sp, idx = INFO[key]; spd = T['P'][cur][1]
            nxt = T['P'][cur + 1][0] if cur + 1 < 5 else T['tree'][0]
            fade = 1 - prog(t, nxt - .35, nxt - .05)
            # row A: key chip -> hashCode
            k = eback(prog(t, ph(cur, 'key'), ph(cur, 'key') + .35 * spd))
            c.save(); c.translate(170, 735); c.scale(k, k)
            kw = F(MONO_B, 34).measureText(f'"{key}"') + 40
            rrect(c, -kw / 2, -30, kw / 2, 30, 16, P(STR, .14 * fade)); rrect(c, -kw / 2, -30, kw / 2, 30, 16, P(STR, .9 * fade, stroke=2))
            text(c, f'"{key}"', 0, 12, F(MONO_B, 34), STR, fade, 'c'); c.restore()
            if t > ph(cur, 'hc'):
                ka = eout(prog(t, ph(cur, 'hc'), ph(cur, 'hc') + .2))
                text(c, '.hashCode()', 300, 747, F(MONO_B, 32), FN, fade * ka)
                pr = prog(t, ph(cur, 'hc'), ph(cur, 'hc_done'))
                if pr < 1:
                    rnd = random.Random(int(t * 30)); val = str(rnd.randint(10**7, 10**9))
                else: val = str(hc)
                text(c, '= ' + val, 520, 747, F(MONO_B, 32), NUM if pr >= 1 else MUTED, fade * ka)
            if t > ph(cur, 'bits'):
                bs = bits_str(sp); n = int(len(bs) * prog(t, ph(cur, 'bits'), ph(cur, 'bits_done')))
                text(c, 'h ^ (h >>> 16)', 80, 800, F(MONO_R, 22), MUTED, fade * eout(prog(t, ph(cur, 'bits'), ph(cur, 'bits') + .2)))
                fb = F(MONO_B, 25)
                text(c, bs[:n], 80, 845, fb, TXT, fade * .85)
                if t > ph(cur, 'mask'):
                    mk = eout(prog(t, ph(cur, 'mask'), ph(cur, 'mask') + .25))
                    x0 = 80 + fb.measureText(bs[:-4]); x1 = x0 + fb.measureText(bs[-4:])
                    rrect(c, x0 - 8, 812, x1 + 8, 858, 10, P(POOL, .5 * mk * fade, blur=10))
                    rrect(c, x0 - 8, 812, x1 + 8, 858, 10, P(POOL, mk * fade, stroke=3))
                    text(c, bs[-4:], x0, 845, fb, POOL, fade)
                    text(c, '& 15', 700, 845, F(MONO_B, 30), POOL, fade * mk)
            if t > ph(cur, 'idx'):
                k = eback(prog(t, ph(cur, 'idx'), ph(cur, 'idx') + .35))
                c.save(); c.translate(920, 790); c.scale(k, k)
                rrect(c, -62, -56, 62, 56, 22, P(POOL, .45 * fade, blur=14)); rrect(c, -62, -56, 62, 56, 22, P('#062420', fade))
                rrect(c, -62, -56, 62, 56, 22, P(POOL, fade, stroke=3))
                text(c, 'bucket', 0, -24, F(INTER_SB, 20), POOL, fade, 'c')
                text(c, str(idx), 0, 34, F(MONO_B, 56), TXT, fade, 'c'); c.restore()

        # bucket rows
        dimk = eio(prog(t, T['dim'], T['dim'] + .4)) * (1 - prog(t, T['tree'][0] - .4, T['tree'][0]))
        for i in range(16):
            k = eout(prog(t, 5.2 + i * .09, 5.5 + i * .09))
            if k <= 0: continue
            y = row_y(i); ra = k * (1 - .7 * dimk if i != 2 else 1)
            flash = 0
            for j in range(4):
                if INFO[ORDER[j]][2] == i and t > ph(j, 'land'): flash = max(flash, math.exp(-(t - ph(j, 'land')) * 3))
            if t > ph(4, 'idx') and i == 2: flash = max(flash, math.exp(-(t - ph(4, 'idx')) * 2))
            rrect(c, 60 - 30 * (1 - k), y, 130 - 30 * (1 - k), y + 42, 10, P(POOL, (.12 + .5 * flash) * ra))
            text(c, str(i), 95 - 30 * (1 - k), y + 31, F(MONO_B, 26), POOL, ra, 'c')
            rrect(c, 142, y, 1020, y + 42, 10, P('#FFFFFF', (.035 + .1 * flash) * ra))
            if i in (1, 2, 15): pass
        lab_a = eout(prog(t, 5.2, 5.8)) * (1 - .7 * dimk)
        text(c, 'table[16]', 1020, 900, F(MONO_B, 24), MUTED, lab_a, 'r')

        # nodes
        for j in range(4):
            key = ORDER[j]; idx = INFO[key][2]
            if t < ph(j, 'fly'): continue
            slot = 0
            sx, sy = 920 - NODE_W / 2, 790 - NODE_H / 2
            tx, ty = slot_x(0), row_y(idx) + 2
            kf = eio(prog(t, ph(j, 'fly'), ph(j, 'land')))
            x = lerp(sx, tx, kf); y = lerp(sy, ty, kf) - math.sin(kf * math.pi) * 120
            col = POOL; glow = 0; sc = lerp(.7, 1, kf)
            if j == 3:
                bump = ph(3, 'land')
                if t > bump:
                    col = FALSEC if t < bump + .5 else POOL
                    sl = eio(prog(t, bump + .35, bump + .75))
                    x = lerp(tx + 18 * math.sin((t - bump) * 50) * math.exp(-(t - bump) * 6), slot_x(1), sl)
                    glow = math.exp(-(t - bump) * 3)
            a_ = 1 - .7 * dimk if idx != 2 else 1
            if j == 2 and t > ph(3, 'land'):  # kiwi shake on hit
                x += 8 * math.sin((t - ph(3, 'land')) * 50) * math.exp(-(t - ph(3, 'land')) * 6)
            # get-phase highlight
            if t > T['cur'] and t < T['tree'][0]:
                if j == 2 and t > T['x1']: col = FALSEC if t < T['mv'] + .3 else MUTED
                if j == 3 and t > T['ok']: col = TRUEC; glow = max(glow, .6)
            node(c, key, x, y, a_ * eout(prog(t, ph(j, 'fly'), ph(j, 'fly') + .15)), sc, col, glow)
        # next arrow kiwi -> lemon
        if t > ph(3, 'land') + .75:
            y = row_y(2) + 21; p_ = eio(prog(t, ph(3, 'land') + .75, ph(3, 'land') + 1.1))
            arrow(c, (slot_x(0) + NODE_W, y), (slot_x(1) - 4, y), VBLUE, p_, w=4)
            text(c, 'next', (slot_x(0) + NODE_W + slot_x(1)) / 2, y - 12, F(MONO_R, 18), MUTED, p_, 'c')
        if t > ph(3, 'land') and t < ph(3, 'land') + 1.2:
            k = eback(prog(t, ph(3, 'land'), ph(3, 'land') + .3)) * (1 - prog(t, ph(3, 'land') + .9, ph(3, 'land') + 1.2))
            c.save(); c.translate(760, row_y(2) + 21); c.scale(k, k)
            rrect(c, -150, -30, 150, 30, 30, P(FALSEC, .25)); rrect(c, -150, -30, 150, 30, 30, P(FALSEC, 1, stroke=3))
            text(c, 'COLLISION!', 0, 11, F(INTER_BLK, 32), FALSEC, 1, 'c', glow=8); c.restore()

        # lookup cursor
        if T['cur'] < t < T['tree'][0] - .2:
            mv = eio(prog(t, T['mv'], T['mv'] + .4))
            k = eback(prog(t, T['cur'], T['cur'] + .3))
            cx = lerp(slot_x(0), slot_x(1), mv) + NODE_W / 2; cy = row_y(2) + 21
            c.save(); c.translate(cx, cy); c.scale(k, k)
            rrect(c, -NODE_W / 2 - 12, -32, NODE_W / 2 + 12, 32, 16, P('#FFFFFF', .9, stroke=3))
            c.restore()
            # verdict tags
            if t > T['x1']:
                kk = eback(prog(t, T['x1'], T['x1'] + .3)) * (1 - .6 * prog(t, T['mv'], T['mv'] + .3))
                verdict(c, slot_x(0) + NODE_W / 2, row_y(3) + 30, False, kk)
            if t > T['ok']:
                kk = eback(prog(t, T['ok'], T['ok'] + .3))
                verdict(c, slot_x(1) + NODE_W / 2, row_y(3) + 30, True, kk)
            # jump beam from pipeline index chip to row 2
            jb = prog(t, T['cur'] - .25, T['cur'] + .05)
            if 0 < jb < 1:
                y = lerp(840, row_y(2) + 21, eio(jb))
                c.drawCircle(lerp(920, slot_x(0) + NODE_W / 2, eio(jb)), y, 18, P('#FFFFFF', .7, blur=8))
        # value fly to result
        if T['val'][0] < t < T['tree'][0]:
            kf = eio(prog(t, *T['val']))
            x = lerp(slot_x(1) + NODE_W - 30, 540, kf); y = lerp(row_y(2) + 28, 1772, kf) - math.sin(kf * math.pi) * 80
            text(c, '4', x, y, F(MONO_B, 40 + 20 * kf), TRUEC, 1, 'c', glow=10)
            if t > T['o1']:
                k = eback(prog(t, T['o1'], T['o1'] + .35)) * (1 - prog(t, T['tree'][0] - .3, T['tree'][0]))
                c.save(); c.translate(820, 1758); c.scale(k, k)
                rrect(c, -150, -36, 150, 32, 30, P(STACK, .18)); rrect(c, -150, -36, 150, 32, 30, P(STACK, 1, stroke=3))
                text(c, 'O(1) average', 0, 10, F(MONO_B, 32), STACK, 1, 'c', glow=8); c.restore()
                text(c, 'get("lemon") =', 300, 1772, F(MONO_B, 40), TXT, k, 'c')

        # ===== tree card =====
        ta = eout(prog(t, T['tree'][0], T['tree'][0] + .4)) * (1 - prog(t, T['tree'][1] - .3, T['tree'][1]))
        if ta > 0:
            card(c, ta, eback(prog(t, T['tree'][0], T['tree'][0] + .5)))
            text(c, 'bucket 2 keeps growing…', W / 2, 860, F(INTER_B, 40), TXT, ta, 'c')
            mo = eio(prog(t, *T['morph']))
            lvl = [(540, 1080), (390, 1220), (690, 1220), (310, 1360), (470, 1360), (610, 1360), (770, 1360), (230, 1500)]
            red = [False, True, True, False, False, False, False, True]
            pts = []
            for i in range(8):
                g = eback(prog(t, lerp(*T['grow'], i / 7), lerp(*T['grow'], i / 7) + .3))
                cx0, cy0 = 175 + i * 104, 1000
                cx, cy = lerp(cx0, lvl[i][0], mo), lerp(cy0, lvl[i][1], mo); pts.append((cx, cy))
            if mo > 0:
                for a_, b_ in [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7)]:
                    c.drawLine(*pts[a_], *pts[b_], P(MUTED, .8 * ta * mo, stroke=3))
            if mo < 1:
                for i in range(7):
                    if t > lerp(*T['grow'], (i + 1) / 7):
                        c.drawLine(pts[i][0] + 34, pts[i][1], pts[i + 1][0] - 34, pts[i + 1][1], P(MUTED, .7 * ta * (1 - mo), stroke=3))
            for i in range(8):
                g = eback(prog(t, lerp(*T['grow'], i / 7), lerp(*T['grow'], i / 7) + .3))
                if g <= 0: continue
                cx, cy = pts[i]; colf = lerp(0, 1, mo)
                fill = FALSEC if (red[i] and mo > .5) else '#1E293B'
                c.drawCircle(cx, cy, 34 * g, P(fill, ta)); c.drawCircle(cx, cy, 34 * g, P('#E8ECF4' if mo > .5 else POOL, ta, stroke=3))
                text(c, 'K' + str(i + 1), cx, cy + 10, F(MONO_B, 26), TXT, ta * g, 'c')
            if t > T['tlab']:
                k = eout(prog(t, T['tlab'], T['tlab'] + .4))
                text(c, 'list → red-black tree', W / 2, 1600, F(INTER_BLK, 46), FALSEC, ta * k, 'c', glow=6)
                text(c, 'lookups stay O(log n)', W / 2, 1660, F(MONO_B, 30), MUTED, ta * k, 'c')
            text(c, 'chain: O(n) to scan' if mo < .5 else '', W / 2, 1120, F(MONO_B, 30), MUTED, ta * (1 - mo) * prog(t, T['grow'][1], T['grow'][1] + .3), 'c')

        # ===== resize card =====
        ra = eout(prog(t, T['rs'][0], T['rs'][0] + .4)) * (1 - prog(t, T['rs'][1] - .3, T['rs'][1]))
        if ra > 0:
            card(c, ra, eback(prog(t, T['rs'][0], T['rs'][0] + .5)))
            text(c, 'load factor = 0.75', W / 2, 860, F(MONO_B, 44), HEAP, ra, 'c')
            dk = eio(prog(t, *T['dbl']))
            n_on = int(12 * prog(t, *T['load']) + 1e-6)
            cw = 48; gap = 4
            # first row: 16 cells shrink width as 32 appear
            ncell = 16 if dk <= 0 else 32
            for i in range(32):
                if i >= 16 and dk <= 0: continue
                rowi, coli = (0, i) if dk <= 0 else (i // 16, i % 16)
                w_ = lerp(cw, cw, 1)
                x0 = 540 - (16 * cw + 15 * gap) / 2 + coli * (cw + gap)
                y0 = lerp(1080, 1040, dk) + rowi * 70
                a_ = ra if i < 16 else ra * dk
                filled = (i < n_on and dk < 1 and t < T['rh'][0])
                rrect(c, x0, y0, x0 + cw, y0 + 56, 8, P(HEAP, (.12 + .5 * filled) * a_))
                rrect(c, x0, y0, x0 + cw, y0 + 56, 8, P(HEAP, .7 * a_, stroke=2))
            text(c, f'{n_on} / 16 full = {int(n_on / 16 * 100)}%' if dk <= 0 else '16  →  32 buckets', W / 2, 1250, F(MONO_B, 40) if dk <= 0 else F(INTER_BLK, 44),
                 TXT if dk <= 0 else STACK, ra, 'c')
            # rehash dots
            if t > T['rh'][0]:
                rk = eio(prog(t, *T['rh']))
                rnd = random.Random(3)
                for e in range(12):
                    src = e; dst = rnd.randrange(32)
                    sx = 540 - (16 * cw + 15 * gap) / 2 + src * (cw + gap) + cw / 2; sy = 1068
                    dx = 540 - (16 * cw + 15 * gap) / 2 + (dst % 16) * (cw + gap) + cw / 2; dy = 1068 + (dst // 16) * 70
                    x = lerp(sx, dx, rk); y = lerp(sy, dy, rk) - math.sin(rk * math.pi) * 60
                    c.drawCircle(x, y, 14, P(POOL, .5 * ra, blur=6)); c.drawCircle(x, y, 9, P(POOL, ra))
                text(c, 'every entry is rehashed', W / 2, 1330, F(INTER_B, 38), MUTED, ra * rk, 'c')
            if dk > 0:
                k = eback(prog(t, T['dbl'][0], T['dbl'][0] + .4))
                c.save(); c.translate(W / 2, 1480); c.scale(k, k)
                text(c, '×2', 0, 0, F(INTER_BLK, 150), STACK, ra, 'c', glow=20); c.restore()

    # captions
    for t0, t1, segs in CAPS:
        if t0 <= t < t1:
            k = eout(prog(t, t0, t0 + .35)) * (1 - prog(t, t1 - .25, t1))
            f = F(INTER_B, 44); w = sum(f.measureText(s) for s, _ in segs)
            y = 1850 if t >= T['lay'][0] else 1640
            x = W / 2 - w / 2; yy = y + 24 * (1 - k)
            rrect(c, x - 28, yy - 52, x + w + 28, yy + 20, 20, P('#050812', .8 * k))
            for s, col in segs: x += text(c, s, x, yy, f, col, k)

    # ===== END CARD =====
    if endk > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P('#050812', .93 * endk))
        e0 = T['end'][0]
        def row(i, y, key, kcol, desc):
            k = eback(prog(t, e0 + .3 + i * .45, e0 + .75 + i * .45)); a = eout(prog(t, e0 + .3 + i * .45, e0 + .6 + i * .45))
            c.save(); c.translate(-80 * (1 - k), 0)
            rrect(c, 90, y - 70, 990, y + 60, 30, P(kcol, .10 * a)); rrect(c, 90, y - 70, 990, y + 60, 30, P(kcol, .8 * a, stroke=3))
            text(c, key, 130, y + 18, F(MONO_B, 56), kcol, a, glow=8)
            text(c, desc, 960, y + 14, F(INTER_B, 42), TXT, a, 'r'); c.restore()
        text(c, 'THE RULE', W / 2, 640, F(INTER_BLK, 40), STACK, eout(prog(t, e0, e0 + .5)), 'c')
        row(0, 820, 'hashCode()', FN, 'picks the bucket')
        row(1, 1010, 'equals()', TRUEC, 'finds the key')
        a2 = eout(prog(t, e0 + 1.6, e0 + 2.1))
        text(c, 'Override them together.', W / 2, 1240, F(INTER_B, 50), TXT, a2, 'c')
        text(c, 'Always.', W / 2, 1320, F(INTER_BLK, 70), STACK, a2, 'c', glow=12)
        a3 = eout(prog(t, e0 + 2.6, e0 + 3.1))
        text(c, 'Save this for your next interview', W / 2, 1560, F(INTER_SB, 38), MUTED, a3, 'c')
        text(c, 'Follow for more Java in 60s', W / 2, 1620, F(INTER_B, 40), POOL, a3, 'c')

    c.drawRect(skia.Rect.MakeWH(W, H), VIG)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 8), P('#FFFFFF', .08))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W * real / DUR, 8), P(POOL, .9))
    fa = max(1 - prog(real, 0, .3), prog(real, DUR - .6, DUR))
    if fa > 0: c.drawRect(skia.Rect.MakeWH(W, H), P('#000000', fa))

VBLUE = '#60A5FA'
WARP = [(0,0),(0.3,0.1),(1.4,1.0),(1.7,1.4),(2.4,2.0),(3.2,2.6),(4.0,3.6),(4.6,4.2),(5.2,5.4),(6.6,6.6),(7.0,7.4),(7.2,7.6),
 (8.4,8.6),(8.5,8.8),(8.8,9.69),(9.3,10.3),(9.5,10.49),(9.9,11.4),(10.0,12.4),(10.3,13.9),(10.7,14.8),(11.3,15.5),(11.6,15.9),
 (12.4,16.4),(13.58,17.12),(14.18,17.8),(14.4,17.85),(15.1,18.1),(16.28,18.66),(16.88,19.3),(17.2,19.45),(18.0,20.0),(19.9,22.0),
 (20.3,22.2),(20.9,22.93),(21.3,24.4),(21.7,24.9),(22.05,25.4),(23.0,26.0),(23.9,26.9),(24.0,27.0),(24.18,27.83),(25.08,28.9),
 (25.3,29.0),(25.5,29.6),(26.0,31.2),(26.6,31.9),(27.0,32.67),(27.4,33.2),(28.2,34.88),(30.0,36.5),(30.4,37.0),(31.6,38.3),
 (31.8,39.6),(32.8,40.5),(33.0,40.8),(34.6,41.4),(35.0,41.8),(36.2,43.3),(36.5,43.9),(37.7,45.0),(38.6,45.6),(40.0,45.9),
 (40.3,46.5),(40.75,48.1),(41.6,48.9),(42.6,49.6),(46,53)]
BEAT = (4.2, 45.9)
def set_warp(w):
    global WA, WU; WA = np.array([a for a, _ in w]); WU = np.array([u for _, u in w])
set_warp(WARP)
def to_audio(t): return float(np.interp(t, WA, WU))
def to_anim(u): return float(np.interp(u, WU, WA))
SURF = skia.Surface(W, H)
def frame(u):
    c = SURF.getCanvas(); c.clear(hexc('#000000')); draw(c, to_anim(u), u)
    return SURF.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)

import math, numpy as np, skia
from anim import (W, H, FPS, F, hexc, P, rrect, text, tokens_draw, eio, eout, eback, prog, lerp, cl, arrow, glowblob,
                  BG, VIG, MONO_B, MONO_R, INTER_BLK, INTER_B, INTER_SB, STACK, POOL, HEAP, TRUEC, FALSEC, TXT, MUTED,
                  PANEL, STR, PUN, ID, FN)
DUR = 36.0
NUM = '#F78C6C'
VB = '#60A5FA'

T = dict(hook=(0.2, 0.7), vs=0.9, wrong=1.8, hout=(3.6, 4.2), lay=(4.2, 6.2),
         acells=(6.4, 7.4), aget=7.8, aform=8.4, ajump=(8.9, 9.5), ao1=9.7,
         ains=10.6, ashift=(11.2, 13.2), adrop=(13.3, 13.7), aon=14.0,
         bnodes=(15.0, 16.6), bins=17.4, bz=17.8, blink=(18.3, 18.9), bhead=(19.0, 19.5), bo1=19.7,
         bget=21.0, bhop=[21.6, 22.3, 23.0, 23.7], bon=24.2,
         cache=25.5, cline=(26.0, 26.8), cmiss=[27.2, 27.6, 28.0, 28.4, 28.8, 29.2, 29.6], cend=30.6,
         end=(31.0, 31.8))
CAPS = [
    (0.0, 3.6, [('Most devs ', TXT), ('pick wrong', FALSEC)]),
    (4.4, 10.4, [('ArrayList: ', STACK), ('side by side', TXT), (' → instant get', TRUEC)]),
    (10.5, 14.9, [('Insert at front → ', TXT), ('everything shifts', FALSEC)]),
    (15.0, 20.8, [('LinkedList: ', VB), ('just relink a pointer', TRUEC)]),
    (20.9, 25.4, [('get(i) → ', TXT), ('walk node by node', FALSEC)]),
    (25.5, 30.9, [('Scattered nodes = ', TXT), ('cache misses', FALSEC)]),
]
SFX = []
def type_ev(t0, t1, s):
    for i, ch in enumerate(s):
        if ch != ' ': SFX.append((t0 + (i + 1) / len(s) * (t1 - t0), 'key'))
SFX += [(T['hook'][0], 'boom'), (T['vs'], 'pop2'), (T['wrong'], 'buzz'), (T['hout'][0], 'whoosh'), (T['lay'][0], 'swell')]
SFX += [(lerp(*T['acells'], i / 7), 'pop') for i in range(6)]
type_ev(T['aget'], T['aget'] + .5, 'list.get(3)'); SFX += [(T['aform'], 'tick'), (T['ajump'][0], 'whoosh'), (T['ajump'][1], 'found'), (T['ao1'], 'ding')]
type_ev(T['ains'], T['ains'] + .5, 'list.add(0, Z)')
SFX += [(lerp(*T['ashift'], i / 6), 'tick') for i in range(6)] + [(T['adrop'][1], 'pop2'), (T['aon'], 'buzz')]
SFX += [(lerp(*T['bnodes'], i / 5), 'pop') for i in range(6)]
type_ev(T['bins'], T['bins'] + .5, 'list.addFirst(Z)')
SFX += [(T['bz'], 'pop2'), (T['blink'][0], 'whoosh'), (T['bhead'][0], 'tick'), (T['bo1'], 'ding')]
type_ev(T['bget'], T['bget'] + .5, 'list.get(3)')
SFX += [(x, 'blip') for x in T['bhop']] + [(T['bon'], 'buzz'), (T['cache'], 'swell'), (T['cline'][0], 'scan'), (T['cline'][1], 'found')]
SFX += [(x, 'tick') for x in T['cmiss']] + [(T['end'][0], 'swell')]

# geometry
A_R = (50, 250, 1030, 880)
B_R = (50, 935, 1030, 1745)
CW = 112; CX0 = 540 - 8 * CW / 2; CY0, CY1 = 470, 590
def cell_x(i): return CX0 + i * CW
VALS = list('ABCDEF')
NODES = [(300, 1110), (600, 1050), (800, 1240), (520, 1350), (230, 1440), (560, 1570)]
ZPOS = (80, 1050)
NW, NH = 160, 66

def badge(c, cx, cy, s, col, k, a=1.0):
    if k <= 0: return
    c.save(); c.translate(cx, cy); c.scale(k, k)
    w = F(MONO_B, 36).measureText(s) + 44
    rrect(c, -w / 2, -32, w / 2, 32, 32, P(col, .18 * a)); rrect(c, -w / 2, -32, w / 2, 32, 32, P(col, a, stroke=3))
    text(c, s, 0, 13, F(MONO_B, 36), col, a, 'c', glow=8); c.restore()

def opchip(c, cx, cy, s, a):
    if a <= 0: return
    f = F(MONO_B, 36); w = f.measureText(s) + 40
    rrect(c, cx - w / 2, cy - 32, cx + w / 2, cy + 30, 14, P('#0A1222', .95 * a)); rrect(c, cx - w / 2, cy - 32, cx + w / 2, cy + 30, 14, P('#33416A', a, stroke=2))
    x = cx - w / 2 + 20
    for part, col in [('list', ID), (s[4:s.index('(')], FN), (s[s.index('('):], NUM)]:
        x += text(c, part, x, cy + 12, f, col, a)

def lnode(c, x, y, val, a, s, col=VB, glow=0.0, nxt=True):
    if a <= 0.01: return
    cx, cy = x + NW / 2, y + NH / 2
    c.save(); c.translate(cx, cy); c.scale(s, s); c.translate(-cx, -cy)
    if glow > 0: rrect(c, x - 8, y - 8, x + NW + 8, y + NH + 8, 18, P(col, .7 * glow * a, blur=14))
    rrect(c, x, y, x + NW, y + NH, 14, P('#0B1424', .96 * a)); rrect(c, x, y, x + NW, y + NH, 14, P(col, .9 * a, stroke=3))
    c.drawLine(x + NW - 52, y + 8, x + NW - 52, y + NH - 8, P(col, .5 * a, stroke=2))
    text(c, val, x + (NW - 52) / 2, y + 46, F(MONO_B, 40), TXT, a, 'c')
    c.drawCircle(x + NW - 26, y + NH / 2, 7, P(col if nxt else MUTED, a))
    c.restore()

def draw(c, t, real):
    c.drawImage(BG, 0, -(t * 1.6) % 40)
    glowblob(c, 180 + 60 * math.sin(t * .3), 520, 520, STACK, .08)
    glowblob(c, 900 + 50 * math.cos(t * .25), 1350, 600, VB, .10)

    # ===== HOOK =====
    ho = 1 - eio(prog(t, *T['hout']))
    if ho > 0:
        c.save(); sc = 1 + .08 * (1 - ho); c.translate(W / 2, H / 2); c.scale(sc, sc); c.translate(-W / 2, -H / 2)
        a = ho
        k1 = eout(prog(t, *T['hook']))
        text(c, 'ArrayList', W / 2 - 600 * (1 - k1), 760, F(MONO_B, 110), STACK, a * k1, 'c', glow=16)
        text(c, 'LinkedList', W / 2 + 600 * (1 - k1), 1120, F(MONO_B, 110), VB, a * k1, 'c', glow=16)
        kv = eback(prog(t, T['vs'], T['vs'] + .4), 2.6)
        c.save(); c.translate(W / 2, 945); c.scale(kv, kv)
        c.drawCircle(0, -30, 78, P(FALSEC, .25 * a)); c.drawCircle(0, -30, 78, P(FALSEC, a, stroke=4))
        text(c, 'VS', 0, 0, F(INTER_BLK, 80), FALSEC, a, 'c'); c.restore()
        text(c, 'JAVA  •  60 SECONDS', W / 2, 400, F(INTER_B, 30), POOL, a * eout(prog(t, 0, .5)), 'c')
        if t > T['wrong']:
            k = eback(prog(t, T['wrong'], T['wrong'] + .35))
            c.save(); c.translate(W / 2, 1380); c.scale(k, k)
            text(c, 'Which one do you use?', 0, 0, F(INTER_B, 54), TXT, a, 'c'); c.restore()
        c.restore()

    if t >= T['lay'][0]:
        ha = eout(prog(t, T['lay'][0], T['lay'][0] + .6))
        c.save(); c.translate(0, -30 * (1 - ha))
        tag = 'JAVA IN 60s'; fw = F(INTER_B, 26).measureText(tag) + 40
        rrect(c, 60, 72, 60 + fw, 116, 22, P(POOL, .15 * ha)); rrect(c, 60, 72, 60 + fw, 116, 22, P(POOL, .8 * ha, stroke=2))
        text(c, tag, 80, 103, F(INTER_B, 26), POOL, ha)
        x = 60 + text(c, 'ArrayList', 60, 196, F(MONO_B, 58), STACK, ha)
        x += text(c, '  vs  ', x, 196, F(INTER_B, 42), MUTED, ha)
        text(c, 'LinkedList', x, 196, F(MONO_B, 58), VB, ha)
        c.restore()

        # panels
        for (l, tp, r, b), col, lab, sub, d in [(A_R, STACK, 'ArrayList', 'one contiguous block', 0), (B_R, VB, 'LinkedList', 'nodes scattered in memory', .2)]:
            k = eio(prog(t, T['lay'][0] + .3 + d, T['lay'][1] + d))
            if k <= 0: continue
            path = skia.Path(); path.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(l, tp, r, b), 28, 28))
            rrect(c, l, tp, r, b, 28, P(col, .05 * k))
            pp = P(col, .7, stroke=3)
            if k < .999: pp.setPathEffect(skia.TrimPathEffect.Make(0, k))
            c.drawPath(path, pp)
            fw = F(MONO_B, 30).measureText(lab) + 36
            rrect(c, l + 24, tp - 22, l + 24 + fw, tp + 22, 22, P('#0A0F1C', k)); rrect(c, l + 24, tp - 22, l + 24 + fw, tp + 22, 22, P(col, k, stroke=2))
            text(c, lab, l + 42, tp + 10, F(MONO_B, 30), col, k)
            text(c, sub, r - 26, tp + 54, F(INTER_SB, 26), MUTED, k, 'r')

        # ---- ArrayList cells ----
        sh = eio(prog(t, *T['ashift']))
        for i in range(8):
            k = eout(prog(t, lerp(*T['acells'], i / 7), lerp(*T['acells'], i / 7) + .3))
            if k <= 0: continue
            x = cell_x(i); y = CY0 + 30 * (1 - k)
            rrect(c, x, y, x + CW, y + (CY1 - CY0), 0, P(STACK, .07 * k))
            rrect(c, x, y, x + CW, y + (CY1 - CY0), 0, P(STACK, .55 * k, stroke=2))
            text(c, f'0x{0x100 + 4 * i:X}', x + CW / 2, CY0 - 16, F(MONO_R, 20), MUTED, k, 'c')
            text(c, f'[{i}]', x + CW / 2, CY1 + 40, F(MONO_B, 26), STACK, k * .9, 'c')
        # values (with shifting)
        for i, v in enumerate(VALS):
            k = eback(prog(t, lerp(*T['acells'], i / 7) + .1, lerp(*T['acells'], i / 7) + .45))
            if k <= 0: continue
            j = 5 - i  # shift order: last element moves first
            mk = eio(prog(t, lerp(*T['ashift'], j / 6), lerp(*T['ashift'], j / 6) + .33))
            x = cell_x(i) + CW / 2 + CW * mk; y = CY0 + 76 - math.sin(mk * math.pi) * 40
            col = TXT
            if T['ajump'][1] < t < T['ains'] and i == 3: col = TRUEC
            if 0 < mk < 1: col = FALSEC
            c.save(); c.translate(x, y - 14); c.scale(k, k)
            text(c, v, 0, 14, F(MONO_B, 54), col, 1, 'c'); c.restore()
        if t > T['adrop'][0]:
            k = eio(prog(t, *T['adrop']))
            text(c, 'Z', cell_x(0) + CW / 2, lerp(CY0 - 100, CY0 + 76, k), F(MONO_B, 54), POOL, k, 'c', glow=10)
        # ArrayList ops
        aop_get = (1 - prog(t, T['ains'] - .3, T['ains'])) * eout(prog(t, T['aget'], T['aget'] + .3))
        opchip(c, 360, 790, 'list.get(3)', aop_get)
        if t > T['aform'] and t < T['ains']:
            ka = eout(prog(t, T['aform'], T['aform'] + .3)) * (1 - prog(t, T['ains'] - .3, T['ains']))
            text(c, 'address = 0x100 + 3 × 4', 540, 700, F(MONO_B, 34), MUTED, ka, 'c')
        if T['ajump'][0] < t < T['ains']:
            jk = eio(prog(t, *T['ajump'])); fade = 1 - prog(t, T['ains'] - .3, T['ains'])
            sx, ex = cell_x(0) + CW / 2, cell_x(3) + CW / 2
            path = skia.Path(); path.moveTo(sx, CY0 - 50)
            x = lerp(sx, ex, jk); yy = CY0 - 50 - math.sin(jk * math.pi) * 90
            path.quadTo((sx + x) / 2, CY0 - 50 - 180 * jk, x, yy)
            c.drawPath(path, P(TRUEC, .5 * fade, stroke=10, blur=6)); c.drawPath(path, P(TRUEC, fade, stroke=4))
            c.drawCircle(x, yy, 10, P('#FFFFFF', fade))
            if jk >= 1:
                rrect(c, cell_x(3) - 4, CY0 - 4, cell_x(4) + 4, CY1 + 4, 6, P(TRUEC, .6 * fade, blur=12))
                rrect(c, cell_x(3), CY0, cell_x(4), CY1, 0, P(TRUEC, fade, stroke=4))
        badge(c, 760, 790, 'O(1)', TRUEC, eback(prog(t, T['ao1'], T['ao1'] + .35)) * (1 - prog(t, T['ains'] - .3, T['ains'])))
        aop_ins = eout(prog(t, T['ains'], T['ains'] + .3)) * (1 - prog(t, T['cache'] - .3, T['cache']))
        opchip(c, 360, 790, 'list.add(0, Z)', aop_ins)
        if T['ashift'][0] < t < T['cache']:
            moves = int(6 * prog(t, *T['ashift']) + 1e-6)
            text(c, f'{moves} elements moved', 540, 700, F(MONO_B, 34), FALSEC, aop_ins, 'c')
        badge(c, 800, 790, 'O(n)', FALSEC, eback(prog(t, T['aon'], T['aon'] + .35)) * (1 - prog(t, T['cache'] - .3, T['cache'])))

        # ---- LinkedList ----
        zin = t > T['bz']
        hk = eio(prog(t, *T['bhead']))
        # arrows between nodes
        for i in range(6):
            kn = eout(prog(t, lerp(*T['bnodes'], i / 5), lerp(*T['bnodes'], i / 5) + .3))
            if i < 5 and kn > 0:
                x0, y0 = NODES[i]; x1, y1 = NODES[i + 1]
                pa = eio(prog(t, lerp(*T['bnodes'], i / 5) + .2, lerp(*T['bnodes'], i / 5) + .55))
                st = (x0 + NW - 26, y0 + NH / 2)
                en = (x1 - 2, y1 + NH / 2) if x1 > x0 + NW else (x1 + NW / 2, y1 - 2) if y1 > y0 else (x1 + NW / 2, y1 + NH + 2)
                hl = 0
                if t > T['bget']:
                    hop = T['bhop']
                    if i < 2 and t > hop[i + 2] and t < T['cache']: hl = 1
                arrow(c, st, en, TRUEC if hl else VB, pa, a=.9, w=4)
        if zin:
            pz = eio(prog(t, *T['blink']))
            zl = T['bhop'][1] < t < T['cache']
            arrow(c, (ZPOS[0] + NW - 26, ZPOS[1] + NH / 2), (NODES[0][0] - 2, NODES[0][1] + NH / 2), TRUEC if zl else POOL, pz, w=4)
        for i, (x, y) in enumerate(NODES):
            kn = eback(prog(t, lerp(*T['bnodes'], i / 5), lerp(*T['bnodes'], i / 5) + .4))
            col = VB; glow = 0
            if t > T['bget'] and t < T['cache']:
                for h_i, ht in enumerate(T['bhop']):
                    if t > ht and h_i == i + 1: col = TRUEC if h_i == 3 else POOL; glow = math.exp(-(t - ht) * 3) + (.5 if h_i == 3 else 0)
            if T['cache'] < t < T['end'][0]:
                for m_i, mt in enumerate(T['cmiss'][:6]):
                    if t > mt and m_i == i: col = FALSEC; glow = math.exp(-(t - mt) * 3)
            lnode(c, x, y, VALS[i], kn, kn, col, glow, nxt=i < 5)
        if zin:
            kz = eback(prog(t, T['bz'], T['bz'] + .4)); zg = math.exp(-(t - T['bz']) * 2)
            if T['bhop'][0] < t < T['cache']: zg = max(zg, math.exp(-(t - T['bhop'][0]) * 3))
            lnode(c, ZPOS[0], ZPOS[1], 'Z', kz, kz, POOL, zg)
        # head pointer
        if t > T['bnodes'][0]:
            ka = eout(prog(t, T['bnodes'][0], T['bnodes'][0] + .4))
            hx = lerp(NODES[0][0] + NW / 2, ZPOS[0] + NW / 2, hk); hy = lerp(NODES[0][1], ZPOS[1], hk)
            text(c, 'head', hx, hy - 52, F(MONO_B, 26), STACK, ka, 'c')
            c.drawLine(hx, hy - 44, hx, hy - 10, P(STACK, ka, stroke=4))
            tri = skia.Path(); tri.moveTo(hx, hy - 4); tri.lineTo(hx - 9, hy - 18); tri.lineTo(hx + 9, hy - 18); tri.close()
            c.drawPath(tri, P(STACK, ka))
        # hop cursor
        if T['bget'] < t < T['cache']:
            hop = T['bhop']; idx = max([i for i, h in enumerate(hop) if t > h] or [-1])
            if idx >= 0:
                x, y = ZPOS if idx == 0 else NODES[idx - 1]
                text(c, f'step {idx + 1}', x + NW / 2, y + NH + 34, F(MONO_B, 24), TRUEC if idx == 3 else POOL, 1, 'c')
        bop1 = eout(prog(t, T['bins'], T['bins'] + .3)) * (1 - prog(t, T['bget'] - .3, T['bget']))
        opchip(c, 360, 1665, 'list.addFirst(Z)', bop1)
        badge(c, 830, 1665, 'O(1)', TRUEC, eback(prog(t, T['bo1'], T['bo1'] + .35)) * (1 - prog(t, T['bget'] - .3, T['bget'])))
        bop2 = eout(prog(t, T['bget'], T['bget'] + .3)) * (1 - prog(t, T['cache'] - .3, T['cache']))
        opchip(c, 360, 1665, 'list.get(3)', bop2)
        badge(c, 760, 1665, 'O(n)', FALSEC, eback(prog(t, T['bon'], T['bon'] + .35)) * (1 - prog(t, T['cache'] - .3, T['cache'])))

        # ---- cache scene ----
        if T['cache'] < t < T['end'][1]:
            ck = eout(prog(t, T['cache'], T['cache'] + .4)) * (1 - prog(t, T['end'][0], T['end'][0] + .4))
            text(c, 'CPU cache', 540, 700, F(INTER_BLK, 34), POOL, ck, 'c')
            sw = eio(prog(t, *T['cline']))
            if sw > 0:
                x1 = lerp(cell_x(0), cell_x(8), sw)
                rrect(c, cell_x(0) - 6, CY0 - 6, x1 + 6, CY1 + 6, 8, P(TRUEC, .5 * ck, blur=14))
                rrect(c, cell_x(0) - 6, CY0 - 6, x1 + 6, CY1 + 6, 8, P(TRUEC, ck, stroke=4))
            if t > T['cline'][1]:
                badge(c, 540, 790, '1 load = all 8 hits', TRUEC, eback(prog(t, T['cline'][1], T['cline'][1] + .35)) * ck)
            misses = sum(1 for m in T['cmiss'][:6] if t > m)
            if misses:
                badge(c, 540, 1665, f'{misses} cache misses', FALSEC, ck)

    # captions
    for t0, t1, segs in CAPS:
        if t0 <= t < t1:
            k = eout(prog(t, t0, t0 + .35)) * (1 - prog(t, t1 - .25, t1))
            f = F(INTER_B, 44); w = sum(f.measureText(s) for s, _ in segs)
            y = 1850 if t >= T['lay'][0] else 1640
            x = W / 2 - w / 2; yy = y + 24 * (1 - k)
            rrect(c, x - 28, yy - 52, x + w + 28, yy + 20, 20, P('#050812', .8 * k))
            for s, col in segs: x += text(c, s, x, yy, f, col, k)

    # ===== END (scoreboard) =====
    endk = eio(prog(t, *T['end']))
    if endk > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P('#050812', .94 * endk))
        e0 = T['end'][0]
        text(c, 'SCOREBOARD', W / 2, 470, F(INTER_BLK, 40), POOL, eout(prog(t, e0, e0 + .5)), 'c')
        hx = [330, 560, 830]
        a0 = eout(prog(t, e0 + .2, e0 + .6))
        text(c, 'ArrayList', hx[1], 580, F(MONO_B, 36), STACK, a0, 'c')
        text(c, 'LinkedList', hx[2], 580, F(MONO_B, 36), VB, a0, 'c')
        rows = [('get(i)', 'O(1)', True, 'O(n)', False), ('add front', 'O(n)', False, 'O(1)', True),
                ('add end', 'O(1)*', True, 'O(1)', True), ('cache', 'friendly', True, 'misses', False),
                ('memory', 'compact', True, '+2 refs/node', False)]
        for i, (lab, a_, ga, b_, gb) in enumerate(rows):
            k = eout(prog(t, e0 + .5 + i * .3, e0 + .8 + i * .3)); y = 690 + i * 110
            rrect(c, 70, y - 55, 1010, y + 40, 18, P('#FFFFFF', .04 * k))
            text(c, lab, 100, y + 8, F(INTER_B, 38), TXT, k)
            text(c, a_, hx[1], y + 8, F(MONO_B, 36), TRUEC if ga else FALSEC, k, 'c')
            text(c, b_, hx[2], y + 8, F(MONO_B, 32 if len(b_) > 6 else 36), TRUEC if gb else FALSEC, k, 'c')
        text(c, '* amortized', 1000, 1300, F(MONO_R, 24), MUTED, eout(prog(t, e0 + 2, e0 + 2.3)), 'r')
        kk = eback(prog(t, e0 + 2.2, e0 + 2.7))
        c.save(); c.translate(W / 2, 1440); c.scale(kk, kk)
        text(c, 'Default to', 0, -60, F(INTER_B, 48), TXT, 1, 'c')
        text(c, 'ArrayList', 0, 40, F(MONO_B, 100), STACK, 1, 'c', glow=18); c.restore()
        a3 = eout(prog(t, e0 + 3.0, e0 + 3.5))
        text(c, 'Save this for your next interview', W / 2, 1660, F(INTER_SB, 36), MUTED, a3, 'c')
        text(c, 'Follow for more Java in 60s', W / 2, 1720, F(INTER_B, 40), POOL, a3, 'c')

    c.drawRect(skia.Rect.MakeWH(W, H), VIG)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 8), P('#FFFFFF', .08))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W * real / DUR, 8), P(POOL, .9))
    fa = max(1 - prog(real, 0, .3), prog(real, DUR - .6, DUR))
    if fa > 0: c.drawRect(skia.Rect.MakeWH(W, H), P('#000000', fa))

WARP = [(0,0),(0.2,0.05),(0.9,0.8),(1.8,2.75),(3.6,4.2),(4.2,4.6),(6.2,5.6),(6.4,5.7),(7.4,7.4),(7.8,7.98),(8.4,8.6),
 (8.9,9.07),(9.5,9.74),(9.7,10.24),(10.6,11.0),(11.2,12.4),(13.2,14.0),(13.3,14.1),(13.7,14.4),(14.0,14.5),(15.0,15.0),
 (16.6,17.0),(17.4,18.3),(17.8,18.9),(18.3,19.6),(18.9,20.3),(19.0,20.4),(19.5,20.8),(19.7,20.94),(21.0,21.6),(21.6,22.8),
 (22.3,23.5),(23.0,23.95),(23.7,24.3),(24.2,24.6),(25.5,25.0),(26.0,25.4),(26.8,26.1),(27.2,26.6),(29.6,28.4),(31.0,28.73),
 (33.2,30.0),(34.0,31.8),(38,36)]
BEAT = (4.6, 28.7)
def set_warp(w):
    global WA, WU; WA = np.array([a for a, _ in w]); WU = np.array([u for _, u in w])
set_warp(WARP)
def to_audio(t): return float(np.interp(t, WA, WU))
def to_anim(u): return float(np.interp(u, WU, WA))
SURF = skia.Surface(W, H)
def frame(u):
    c = SURF.getCanvas(); c.clear(hexc('#000000')); draw(c, to_anim(u), u)
    return SURF.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)

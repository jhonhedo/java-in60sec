import math, skia, numpy as np

W, H, FPS = 1080, 1920, 30
DUR = 50.0

import os
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts') + '/'
MONO_B = skia.Typeface.MakeFromFile(FD + 'jetbrains-mono-latin-700-normal.woff')
MONO_R = skia.Typeface.MakeFromFile(FD + 'jetbrains-mono-latin-400-normal.woff')
INTER_BLK = skia.Typeface.MakeFromFile(FD + 'Inter-Black.otf')
INTER_B = skia.Typeface.MakeFromFile(FD + 'Inter-Bold.otf')
INTER_SB = skia.Typeface.MakeFromFile(FD + 'Inter-SemiBold.otf')

def F(tf, size):
    f = skia.Font(tf, size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias); return f

def hexc(h, a=1.0):
    h = h.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.ColorSetARGB(int(max(0, min(1, a)) * 255), r, g, b)

BG1, BG2 = '#070B16', '#101A33'
STACK, POOL, HEAP = '#FFB547', '#2DD4BF', '#A78BFA'
TRUEC, FALSEC = '#4ADE80', '#F87171'
TXT, MUTED, PANEL = '#E8ECF4', '#6B7894', '#0D1426'
VA, VB, VC = '#FFB547', '#60A5FA', '#F472B6'
KW, KW2, STR, OP, PUN, ID, FN = '#7DD3FC', '#F472B6', '#A5E075', '#89DDFF', '#94A3B8', '#E8ECF4', '#FCD34D'

# ---------- easing ----------
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return cl((t - a) / (b - a)) if b > a else float(t >= a)
def eio(x): x = cl(x); return 4*x*x*x if x < .5 else 1 - (-2*x + 2)**3 / 2
def eout(x): x = cl(x); return 1 - (1 - x)**3
def eback(x, s=1.9): x = cl(x); x -= 1; return x*x*((s+1)*x + s) + 1
def lerp(a, b, x): return a + (b - a) * x

# ---------- timeline ----------
T = dict(
    h1=(0.35, 1.5), h1r=1.85, h2=(2.35, 3.9), h2r=4.25, why=4.7, hout=(5.25, 5.85),
    lay=(5.85, 8.6),
    l1=(9.0, 10.4), sa=10.6, oa=11.15, ca=11.7, arA=(11.9, 12.7),
    l2=(14.2, 15.6), sb=15.8, scan=(16.1, 17.2), found=17.25, arB=(17.5, 18.3), cb=18.35,
    cmp1=(19.2, 19.9), cmp1r=20.35,
    l3=(22.0, 24.0), sc=24.2, oc=24.75, cc=25.3, arC=(25.5, 26.3),
    cmp2=(27.2, 27.9), cmp2r=28.35,
    eq=(30.2, 30.9), eqc=[31.3, 31.8, 32.3, 32.8], eqr=33.35,
    l4=(36.4, 37.6), swing=(38.1, 39.2), cc2=39.25, gc=39.9, cmp3=(40.6, 41.0), cmp3r=41.3,
    end=(42.8, 43.6),
)

SFX = []  # (time, kind)

def type_ev(rng, text, kind='key'):
    n = len(text)
    for i in range(n):
        if text[i] != ' ':
            SFX.append((rng[0] + (i + 1) / n * (rng[1] - rng[0]), kind))

# code tokens
L = [
    [('String', KW), (' a ', ID), ('=', OP), (' ', ID), ('"java"', STR), (';', PUN)],
    [('String', KW), (' b ', ID), ('=', OP), (' ', ID), ('"java"', STR), (';', PUN)],
    [('String', KW), (' c ', ID), ('=', OP), (' ', ID), ('new', KW2), (' ', ID), ('String', KW), ('(', PUN), ('"java"', STR), (');', PUN)],
    [('c ', ID), ('=', OP), (' c.', ID), ('intern', FN), ('();', PUN)],
]
LT = [T['l1'], T['l2'], T['l3'], T['l4']]
H1 = [('"java"', STR), (' == ', OP), ('"java"', STR)]
H2 = [('new', KW2), (' ', ID), ('String', KW), ('(', PUN), ('"java"', STR), (')', PUN), (' == ', OP), ('"java"', STR)]
def txt(tokens): return ''.join(s for s, _ in tokens)

for toks, rng in [(H1, T['h1']), (H2, T['h2'])] + list(zip(L, LT)):
    type_ev(rng, txt(toks))
CMPS = [('a == b', T['cmp1'], T['cmp1r'], True, '@7a1 == @7a1'),
        ('a == c', T['cmp2'], T['cmp2r'], False, '@7a1 == @3f9'),
        ('a.equals(c)', T['eq'], T['eqr'], True, '"java" vs "java"'),
        ('a == c', T['cmp3'], T['cmp3r'], True, '@7a1 == @7a1')]
for s, rng, r, ok, _ in CMPS:
    type_ev(rng, s); SFX.append((r, 'ding' if ok else 'buzz'))
SFX += [(T['h1r'], 'ding'), (T['h2r'], 'buzz'), (T['why'], 'boom'), (T['hout'][0], 'whoosh'),
        (T['lay'][0], 'swell'), (T['sa'], 'pop'), (T['oa'], 'pop2'), (T['ca'], 'tick'), (T['arA'][0], 'whoosh'),
        (T['sb'], 'pop'), (T['scan'][0], 'scan'), (T['found'], 'found'), (T['arB'][0], 'whoosh'), (T['cb'], 'tick'),
        (T['sc'], 'pop'), (T['oc'], 'pop2'), (T['cc'], 'tick'), (T['arC'][0], 'whoosh'),
        (T['swing'][0], 'whoosh'), (T['cc2'], 'tick'), (T['gc'], 'down'), (T['end'][0], 'swell')]
SFX += [(x, 'blip') for x in T['eqc']]

CAPS = [
    (0.0, 5.2, [('Same text. ', TXT), ('Different answer.', FALSEC)]),
    (6.0, 8.9, [('Let\'s look ', TXT), ('inside memory', POOL)]),
    (9.0, 14.0, [('String literals live in the ', TXT), ('String Pool', POOL)]),
    (14.2, 19.0, [('Same literal? Java ', TXT), ('reuses', POOL), (' the object', TXT)]),
    (19.1, 21.8, [('==', STACK), (' compares the ', TXT), ('references', STACK)]),
    (22.0, 27.0, [('new', KW2), (' always creates a ', TXT), ('fresh object', HEAP)]),
    (27.1, 30.0, [('Different address → ', TXT), ('false', FALSEC)]),
    (30.1, 36.2, [('.equals()', POOL), (' compares the ', TXT), ('characters', TRUEC)]),
    (36.3, 42.6, [('intern()', FN), (' hands back the ', TXT), ('pooled copy', POOL)]),
]

# ---------- geometry ----------
STACK_R = (50, 760, 340, 1560)
HEAP_R = (370, 760, 1030, 1560)
POOL_R = (395, 808, 1005, 1140)
OBJ_W, OBJ_H = 400, 180
OA = (705, 885)    # pool object (cx, top)
OC = (705, 1300)   # heap object
SLOTS = {'a': 820, 'b': 970, 'c': 1120}
SLOT_X0, SLOT_X1, SLOT_H = 72, 318, 120

# ---------- drawing helpers ----------
def P(color, a=1.0, stroke=0, blur=0):
    p = skia.Paint(AntiAlias=True, Color=hexc(color, a))
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p

def rrect(c, l, t, r, b, rad, paint): c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(l, t, r, b), rad, rad), paint)

def text(c, s, x, y, font, color, a=1.0, align='l', glow=0):
    w = font.measureText(s)
    if align == 'c': x -= w / 2
    elif align == 'r': x -= w
    if glow: c.drawString(s, x, y, font, P(color, a * 0.7, blur=glow))
    c.drawString(s, x, y, font, P(color, a))
    return w

def tokens_draw(c, toks, n, x, y, font, a=1.0):
    for s, col in toks:
        if n <= 0: break
        part = s[:n]; n -= len(s)
        x += text(c, part, x, y, font, col, a)
    return x

def bez_split(p0, p1, p2, p3, t):
    L_ = lambda a, b: (lerp(a[0], b[0], t), lerp(a[1], b[1], t))
    p01, p12, p23 = L_(p0, p1), L_(p1, p2), L_(p2, p3)
    p012, p123 = L_(p01, p12), L_(p12, p23)
    return p0, p01, p012, L_(p012, p123)

def arrow(c, start, end, color, p, a=1.0, w=6):
    if p <= 0: return
    dx = end[0] - start[0]
    p1 = (start[0] + dx * 0.55, start[1]); p2 = (end[0] - dx * 0.55, end[1])
    q0, q1, q2, q3 = bez_split(start, p1, p2, end, p)
    path = skia.Path(); path.moveTo(*q0); path.cubicTo(*q1, *q2, *q3)
    c.drawPath(path, P(color, a * 0.45, stroke=w + 8, blur=7))
    c.drawPath(path, P(color, a, stroke=w))
    ang = math.atan2(q3[1] - q2[1], q3[0] - q2[0])
    s = 22 * eout(prog(p, 0.0, 0.3))
    tri = skia.Path(); tri.moveTo(*q3)
    tri.lineTo(q3[0] - s * math.cos(ang - 0.45), q3[1] - s * math.sin(ang - 0.45))
    tri.lineTo(q3[0] - s * math.cos(ang + 0.45), q3[1] - s * math.sin(ang + 0.45)); tri.close()
    c.drawPath(tri, P(color, a))
    c.drawCircle(*start, 8, P(color, a))

def obj_card(c, cx, top, addr, color, a=1.0, s=1.0, pulse=0.0, cells_on=None):
    if a <= 0.01 or s <= 0.01: return
    c.save(); c.translate(cx, top + OBJ_H / 2); c.scale(s, s); c.translate(-cx, -(top + OBJ_H / 2))
    l, r, b = cx - OBJ_W / 2, cx + OBJ_W / 2, top + OBJ_H
    if pulse > 0: rrect(c, l - 6, top - 6, r + 6, b + 6, 26, P(color, 0.55 * pulse * a, blur=22))
    rrect(c, l, top, r, b, 22, P('#0B1222', 0.96 * a))
    rrect(c, l, top, r, b, 22, P(color, (0.55 + 0.45 * pulse) * a, stroke=3))
    text(c, 'String object', l + 22, top + 42, F(INTER_SB, 26), MUTED, a)
    text(c, addr, r - 22, top + 43, F(MONO_B, 30), color, a, 'r')
    cw, ch, gap = 80, 92, 12; x0 = cx - (4 * cw + 3 * gap) / 2
    for i, ch_ in enumerate('java'):
        x = x0 + i * (cw + gap); y = top + 66
        on = cells_on[i] if cells_on else 0
        rrect(c, x, y, x + cw, y + ch, 14, P(TRUEC if on else color, (0.10 + 0.18 * on) * a))
        rrect(c, x, y, x + cw, y + ch, 14, P(TRUEC if on else color, (0.35 + 0.6 * on) * a, stroke=2))
        text(c, ch_, x + cw / 2, y + 64, F(MONO_B, 50), TXT, a, 'c')
    c.restore()

def slot(c, name, y, color, addr, addr_col, a, s, glow=0.0, addr_a=1.0, addr2=None, mix=0.0, shake=0.0):
    if a <= 0.01: return
    cx, cy = (SLOT_X0 + SLOT_X1) / 2, y + SLOT_H / 2
    c.save(); c.translate(cx + shake, cy); c.scale(s, s); c.translate(-cx, -cy)
    rrect(c, SLOT_X0, y, SLOT_X1, y + SLOT_H, 18, P('#140F05', 0.9 * a))
    rrect(c, SLOT_X0, y, SLOT_X1, y + SLOT_H, 18, P(color, 0.6 * a, stroke=3))
    text(c, name, SLOT_X0 + 34, y + 80, F(MONO_B, 58), color, a, 'c' if False else 'l')
    chx0, chx1, chy0, chy1 = 158, 302, y + 30, y + 90
    if glow > 0: rrect(c, chx0 - 8, chy0 - 8, chx1 + 8, chy1 + 8, 18, P(addr_col, 0.8 * glow * a, blur=16))
    rrect(c, chx0, chy0, chx1, chy1, 12, P(addr_col, (0.14 + 0.2 * glow) * a * addr_a))
    rrect(c, chx0, chy0, chx1, chy1, 12, P(addr_col, 0.8 * a * addr_a, stroke=2))
    if addr2 is None:
        text(c, addr, (chx0 + chx1) / 2, chy0 + 41, F(MONO_B, 30), addr_col, a * addr_a, 'c')
    else:
        c.save(); c.clipRect(skia.Rect.MakeLTRB(chx0, chy0, chx1, chy1))
        text(c, addr, (chx0 + chx1) / 2, chy0 + 41 - 60 * mix, F(MONO_B, 30), HEAP, a, 'c')
        text(c, addr2, (chx0 + chx1) / 2, chy0 + 41 + 60 * (1 - mix), F(MONO_B, 30), POOL, a, 'c')
        c.restore()
    c.restore()

# ---------- background ----------
def make_bg():
    s = skia.Surface(W, H + 80); c = s.getCanvas()
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (W, H)], [hexc(BG1), hexc(BG2)]))
    c.drawRect(skia.Rect.MakeWH(W, H + 80), p)
    dp = P('#8AA0D0', 0.10)
    for gy in range(0, H + 80, 40):
        for gx in range(20, W, 40): c.drawCircle(gx, gy, 1.6, dp)
    return s.makeImageSnapshot()
BG = make_bg()
VIG = skia.Paint(Shader=skia.GradientShader.MakeRadial((W / 2, H / 2), H * 0.75,
                 [hexc('#000000', 0), hexc('#000000', 0.55)]))

def glowblob(c, x, y, r, col, a):
    c.drawCircle(x, y, r, skia.Paint(Shader=skia.GradientShader.MakeRadial((x, y), r, [hexc(col, a), hexc(col, 0)])))

# ---------- frame ----------
def draw(c, t):
    c.drawImage(BG, 0, -(t * 1.6) % 40)
    glowblob(c, 180 + 60 * math.sin(t * 0.3), 420, 520, POOL, 0.10)
    glowblob(c, 920 + 50 * math.cos(t * 0.25), 1350, 600, HEAP, 0.10)

    # ===== HOOK =====
    ho = 1 - eio(prog(t, *T['hout']))
    if ho > 0:
        c.save(); sc = 1 + 0.08 * (1 - ho); c.translate(W / 2, H / 2); c.scale(sc, sc); c.translate(-W / 2, -H / 2)
        a = ho
        text(c, 'JAVA  •  60 SECONDS', W / 2, 330, F(INTER_B, 30), POOL, a * eout(prog(t, 0, 0.5)), 'c')
        fm = F(MONO_B, 56)
        for toks, rng, ry, rt, ok in [(H1, T['h1'], 720, T['h1r'], True), (H2, T['h2'], 960, T['h2r'], False)]:
            s_ = txt(toks); n = int(len(s_) * prog(t, *rng) + 1e-6)
            if t < rng[0]: continue
            w = fm.measureText(s_); x0 = W / 2 - w / 2
            sh = 0 if ok else 14 * math.sin((t - rt) * 60) * math.exp(-(t - rt) * 6) * (t > rt)
            x = tokens_draw(c, toks, n, x0 + sh, ry, fm, a)
            if n < len(s_) and int(t * 4) % 2 == 0: rrect(c, x + 3, ry - 46, x + 9, ry + 10, 2, P(TXT, a))
            if t > rt:
                k = eback(prog(t, rt, rt + 0.35)); col = TRUEC if ok else FALSEC
                lab = 'true' if ok else 'false'
                c.save(); c.translate(W / 2, ry + 95); c.scale(k, k)
                fw = F(MONO_B, 48).measureText(lab) + 60
                rrect(c, -fw / 2, -40, fw / 2, 30, 35, P(col, 0.18 * a))
                rrect(c, -fw / 2, -40, fw / 2, 30, 35, P(col, 0.9 * a, stroke=3))
                text(c, lab, 0, 13, F(MONO_B, 48), col, a, 'c', glow=10)
                c.restore()
        if t > T['why']:
            k = eback(prog(t, T['why'], T['why'] + 0.4), 2.6)
            c.save(); c.translate(W / 2, 1380); c.scale(k, k)
            text(c, 'WHY?', 0, 0, F(INTER_BLK, 210), STACK, a, 'c', glow=30)
            c.restore()
        c.restore()

    # ===== MAIN LAYOUT =====
    lay = prog(t, *T['lay'])
    endk = eio(prog(t, *T['end']))
    if lay > 0:
        # header
        ha = eout(prog(t, T['lay'][0], T['lay'][0] + 0.6))
        c.save(); c.translate(0, -30 * (1 - ha))
        tag = 'JAVA IN 60s'; fw = F(INTER_B, 26).measureText(tag) + 40
        rrect(c, 60, 72, 60 + fw, 116, 22, P(POOL, 0.15 * ha)); rrect(c, 60, 72, 60 + fw, 116, 22, P(POOL, 0.8 * ha, stroke=2))
        text(c, tag, 80, 103, F(INTER_B, 26), POOL, ha)
        x = 60
        for s_, col in [('==', STACK), ('  vs  ', MUTED), ('.equals()', POOL)]:
            x += text(c, s_, x, 196, F(MONO_B, 64) if col != MUTED else F(INTER_B, 46), col, ha)
        c.restore()

        # code panel
        ca = eout(prog(t, T['lay'][0] + 0.2, T['lay'][0] + 0.9))
        c.save(); c.translate(0, 40 * (1 - ca))
        rrect(c, 50, 232, 1030, 640, 28, P(PANEL, 0.92 * ca))
        rrect(c, 50, 232, 1030, 640, 28, P('#2A3654', ca, stroke=2))
        for i, col in enumerate(['#FF5F57', '#FEBC2E', '#28C840']): c.drawCircle(88 + i * 30, 268, 9, P(col, ca))
        text(c, 'Main.java', 540, 277, F(INTER_SB, 24), MUTED, ca, 'c')
        fm = F(MONO_B, 37); active = None
        for i, (toks, rng) in enumerate(zip(L, LT)):
            if t >= rng[0] - 0.15: active = i
        for i, (toks, rng) in enumerate(zip(L, LT)):
            y = 350 + i * 72
            if i == active:
                hk = eout(prog(t, rng[0] - 0.15, rng[0] + 0.15))
                rrect(c, 62, y - 44, 1018, y + 20, 12, P('#1C2847', 0.9 * hk * ca))
                rrect(c, 62, y - 44, 68, y + 20, 3, P(POOL, hk * ca))
            text(c, str(i + 1), 104, y, F(MONO_R, 30), MUTED, ca * (1 if t >= rng[0] else 0.35), 'r')
            if t >= rng[0]:
                s_ = txt(toks); n = int(len(s_) * prog(t, *rng) + 1e-6)
                x = tokens_draw(c, toks, n, 135, y, fm, ca)
                if i == active and (n < len(s_) or int(t * 2.2) % 2 == 0) and t < 42.5:
                    rrect(c, x + 3, y - 34, x + 7, y + 8, 2, P(POOL, ca))
        c.restore()

        # memory panels (stroke draw-on)
        ma = eio(prog(t, T['lay'][0] + 0.6, T['lay'][1]))
        for (l, tp, r, b), col, lab, d in [(STACK_R, STACK, 'STACK', 0), (HEAP_R, HEAP, 'HEAP', 0.15)]:
            k = eio(prog(t, T['lay'][0] + 0.6 + d, T['lay'][1] - 0.4 + d))
            if k <= 0: continue
            path = skia.Path(); path.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(l, tp, r, b), 26, 26))
            rrect(c, l, tp, r, b, 26, P(col, 0.05 * k))
            pp = P(col, 0.75, stroke=3)
            if k < 0.999: pp.setPathEffect(skia.TrimPathEffect.Make(0, k))
            c.drawPath(path, pp)
            text(c, lab, l + 22, tp - 14, F(INTER_BLK, 28), col, k)
        k = eio(prog(t, T['lay'][0] + 1.2, T['lay'][1]))
        if k > 0:
            l, tp, r, b = POOL_R
            rrect(c, l, tp, r, b, 22, P(POOL, 0.07 * k))
            pp = P(POOL, 0.85 * k, stroke=3); pp.setPathEffect(skia.DashPathEffect.Make([18, 12], -t * 30))
            rrect(c, l, tp, r, b, 22, pp)
            fw = F(INTER_BLK, 24).measureText('STRING POOL') + 32
            rrect(c, l + 18, tp - 20, l + 18 + fw, tp + 20, 20, P('#07211F', k)); rrect(c, l + 18, tp - 20, l + 18 + fw, tp + 20, 20, P(POOL, k, stroke=2))
            text(c, 'STRING POOL', l + 34, tp + 9, F(INTER_BLK, 24), POOL, k)
            text(c, 'heap', HEAP_R[2] - 24, HEAP_R[3] - 24, F(INTER_SB, 24), HEAP, k * 0.6, 'r')

        # scan beam
        if T['scan'][0] < t < T['scan'][1] + 0.3:
            sk = prog(t, *T['scan']); fade = 1 - prog(t, T['scan'][1], T['scan'][1] + 0.3)
            x = lerp(POOL_R[0] + 10, POOL_R[2] - 10, eio(sk))
            c.save(); c.clipRect(skia.Rect.MakeLTRB(*POOL_R))
            sp = skia.Paint(Shader=skia.GradientShader.MakeLinear([(x - 120, 0), (x, 0)], [hexc(POOL, 0), hexc(POOL, 0.35 * fade)]))
            c.drawRect(skia.Rect.MakeLTRB(x - 120, POOL_R[1], x, POOL_R[3]), sp)
            c.drawRect(skia.Rect.MakeLTRB(x - 2, POOL_R[1], x + 2, POOL_R[3]), P(POOL, fade))
            c.restore()

        # objects
        pulseA = 0.0
        for tp_ in [T['found'], T['cmp1r'], T['cmp3r']]:
            if t > tp_: pulseA = max(pulseA, math.exp(-(t - tp_) * 2.2))
        cells = [eout(prog(t, x, x + 0.25)) for x in T['eqc']] if t > T['eqc'][0] else None
        cellsA = cells if (cells and t < T['l4'][0]) else None
        obj_card(c, *OA, '@7a1', POOL, eout(prog(t, T['oa'], T['oa'] + 0.25)), eback(prog(t, T['oa'], T['oa'] + 0.45)), pulseA, cellsA)
        gcd = eio(prog(t, T['gc'], T['gc'] + 0.6))
        pulseC = math.exp(-(t - T['cmp2r']) * 2.2) if t > T['cmp2r'] else 0
        obj_card(c, *OC, '@3f9', HEAP, eout(prog(t, T['oc'], T['oc'] + 0.25)) * (1 - 0.65 * gcd), eback(prog(t, T['oc'], T['oc'] + 0.45)) * (1 - 0.06 * gcd), pulseC, cellsA)
        if gcd > 0:
            text(c, 'no references → garbage collected', OC[0], OC[1] + OBJ_H + 52, F(INTER_SB, 28), MUTED, gcd, 'c')

        # equals connectors
        if cellsA:
            cw, gap = 80, 12; x0 = OA[0] - (4 * cw + 3 * gap) / 2
            for i, k in enumerate(cells):
                if k <= 0: continue
                x = x0 + i * (cw + gap) + cw / 2; y0 = OA[1] + OBJ_H; y1 = OC[1]
                ym = lerp(y0, y1, k)
                c.drawLine(x, y0, x, ym, P(TRUEC, 0.5, stroke=10, blur=6)); c.drawLine(x, y0, x, ym, P(TRUEC, 1, stroke=4))
                if k > 0.95:
                    mid = (y0 + y1) / 2; kk = eback(prog(t, T['eqc'][i] + 0.2, T['eqc'][i] + 0.45))
                    c.drawCircle(x, mid, 24 * kk, P('#06210F')); c.drawCircle(x, mid, 24 * kk, P(TRUEC, stroke=3))
                    pth = skia.Path(); pth.moveTo(x - 10 * kk, mid); pth.lineTo(x - 3 * kk, mid + 8 * kk); pth.lineTo(x + 11 * kk, mid - 8 * kk)
                    c.drawPath(pth, P(TRUEC, stroke=4))

        # stack slots + arrows
        def glowk(times):
            g = 0
            for tt in times:
                if t > tt: g = max(g, math.exp(-(t - tt) * 1.6))
            return g
        cmpA = glowk([T['cmp1r'], T['cmp2r'], T['cmp3r']]); cmpB = glowk([T['cmp1r']]); cmpC = glowk([T['cmp2r'], T['cmp3r']])
        sh2 = 10 * math.sin((t - T['cmp2r']) * 55) * math.exp(-(t - T['cmp2r']) * 5) if t > T['cmp2r'] else 0
        sw = eio(prog(t, *T['swing']))
        # arrows first (under cards' edges)
        eA, eB = (OA[0] - OBJ_W / 2, OA[1] + 60), (OA[0] - OBJ_W / 2, OA[1] + 120)
        eC0, eC1 = (OC[0] - OBJ_W / 2, OC[1] + 90), (OA[0] - OBJ_W / 2, OA[1] + 150)
        arrow(c, (302, SLOTS['a'] + 60), eA, VA, eio(prog(t, *T['arA'])))
        arrow(c, (302, SLOTS['b'] + 60), eB, VB, eio(prog(t, *T['arB'])))
        if t > T['arC'][0]:
            if sw <= 0: arrow(c, (302, SLOTS['c'] + 60), eC0, VC, eio(prog(t, *T['arC'])))
            else:
                # swinging: retract old & grow new
                if sw < 1: arrow(c, (302, SLOTS['c'] + 60), eC0, VC, 1 - eio(prog(sw, 0, 0.5)), a=0.8)
                arrow(c, (302, SLOTS['c'] + 60), eC1, VC, eio(prog(sw, 0.4, 1)))
        # redraw object borders above arrow heads for neatness not needed
        slot(c, 'a', SLOTS['a'], VA, '@7a1', POOL, eout(prog(t, T['sa'], T['sa'] + .25)), eback(prog(t, T['sa'], T['sa'] + .4)),
             cmpA, addr_a=eout(prog(t, T['ca'], T['ca'] + .3)))
        slot(c, 'b', SLOTS['b'], VB, '@7a1', POOL, eout(prog(t, T['sb'], T['sb'] + .25)), eback(prog(t, T['sb'], T['sb'] + .4)),
             cmpB, addr_a=eout(prog(t, T['cb'], T['cb'] + .3)))
        if t < T['cc2']:
            slot(c, 'c', SLOTS['c'], VC, '@3f9', HEAP, eout(prog(t, T['sc'], T['sc'] + .25)), eback(prog(t, T['sc'], T['sc'] + .4)),
                 cmpC, addr_a=eout(prog(t, T['cc'], T['cc'] + .3)), shake=sh2)
        else:
            slot(c, 'c', SLOTS['c'], VC, '@3f9', POOL, 1, 1, cmpC, addr2='@7a1', mix=eio(prog(t, T['cc2'], T['cc2'] + 0.4)))

        # traveling pulses on compare
        for tt, names in [(T['cmp1r'] - 0.45, 'ab'), (T['cmp2r'] - 0.45, 'ac'), (T['cmp3r'] - 0.3, 'ac')]:
            k = prog(t, tt, tt + 0.45)
            if 0 < k < 1:
                for nm in names:
                    st = (302, SLOTS[nm] + 60)
                    en = {'a': eA, 'b': eB, 'c': (eC0 if tt < 30 else eC1)}[nm]
                    dx = en[0] - st[0]
                    _, _, _, pt = bez_split(st, (st[0] + dx * .55, st[1]), (en[0] - dx * .55, en[1]), en, eio(k))
                    c.drawCircle(*pt, 16, P('#FFFFFF', 0.7, blur=8)); c.drawCircle(*pt, 7, P('#FFFFFF'))

        # bottom: compare result
        cur = None
        for i, (s_, rng, rt, ok, eqs) in enumerate(CMPS):
            nxt = (T['l4'][0] if i == 2 else T['l3'][0] if i == 0 else CMPS[i + 1][1][0]) if i + 1 < len(CMPS) else T['end'][0]
            if rng[0] <= t < nxt - 0.05: cur = (s_, rng, rt, ok, eqs, nxt)
        if cur:
            s_, rng, rt, ok, eqs, nxt = cur
            out = 1 - prog(t, nxt - 0.35, nxt - 0.05)
            fm = F(MONO_B, 54); n = int(len(s_) * prog(t, *rng) + 1e-6)
            lab = 'true' if ok else 'false'; col = TRUEC if ok else FALSEC
            wl = F(MONO_B, 46).measureText(lab) + 56
            total = fm.measureText(s_) + 40 + wl
            x0 = W / 2 - total / 2; y = 1672
            toks = [(ch, STACK if ch in '=' else (POOL if s_.startswith('a.e') and ch not in 'ac()' else TXT)) for ch in s_]
            x = tokens_draw(c, toks, n, x0, y, fm, out)
            if t > rt:
                k = eback(prog(t, rt, rt + 0.35)); shx = 0 if ok else 12 * math.sin((t - rt) * 55) * math.exp(-(t - rt) * 5)
                cx = x0 + fm.measureText(s_) + 40 + wl / 2 + shx
                c.save(); c.translate(cx, y - 18); c.scale(k, k)
                rrect(c, -wl / 2, -38, wl / 2, 34, 34, P(col, 0.2 * out)); rrect(c, -wl / 2, -38, wl / 2, 34, 34, P(col, out, stroke=3))
                text(c, lab, 0, 16, F(MONO_B, 46), col, out, 'c', glow=10)
                c.restore()
                text(c, eqs, W / 2, 1738, F(MONO_R, 32), MUTED, out * eout(prog(t, rt, rt + 0.4)), 'c')

    # captions
    for t0, t1, segs in CAPS:
        if t0 <= t < t1:
            k = eout(prog(t, t0, t0 + 0.35)) * (1 - prog(t, t1 - 0.25, t1))
            f = F(INTER_B, 44); w = sum(f.measureText(s) for s, _ in segs)
            y = 1830 if t >= 5.85 else 1640
            x = W / 2 - w / 2; yy = y + 24 * (1 - k)
            rrect(c, x - 28, yy - 52, x + w + 28, yy + 20, 20, P('#050812', 0.75 * k))
            for s, col in segs: x += text(c, s, x, yy, f, col, k)

    # ===== END CARD =====
    if endk > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P('#050812', 0.93 * endk))
        def row(i, y, key, kcol, desc):
            k = eback(prog(t, T['end'][0] + 0.3 + i * 0.45, T['end'][0] + 0.75 + i * 0.45))
            a = eout(prog(t, T['end'][0] + 0.3 + i * 0.45, T['end'][0] + 0.6 + i * 0.45))
            c.save(); c.translate(-80 * (1 - k), 0)
            rrect(c, 90, y - 70, 990, y + 60, 30, P(kcol, 0.10 * a)); rrect(c, 90, y - 70, 990, y + 60, 30, P(kcol, 0.8 * a, stroke=3))
            text(c, key, 130, y + 20, F(MONO_B, 64), kcol, a, glow=8)
            text(c, desc, 960, y + 16, F(INTER_B, 44), TXT, a, 'r')
            c.restore()
        a0 = eout(prog(t, T['end'][0], T['end'][0] + 0.5))
        text(c, 'THE RULE', W / 2, 640, F(INTER_BLK, 40), STACK, a0, 'c')
        row(0, 820, '==', STACK, 'same object?')
        row(1, 1010, '.equals()', POOL, 'same characters?')
        a2 = eout(prog(t, T['end'][0] + 1.5, T['end'][0] + 2.0))
        text(c, 'Compare Strings with', W / 2, 1230, F(INTER_B, 50), TXT, a2, 'c')
        k3 = eback(prog(t, T['end'][0] + 1.8, T['end'][0] + 2.3))
        c.save(); c.translate(W / 2, 1320); c.scale(k3, k3)
        text(c, '.equals()', 0, 0, F(MONO_B, 96), TRUEC, a2, 'c', glow=18); c.restore()
        a3 = eout(prog(t, T['end'][0] + 2.8, T['end'][0] + 3.3))
        text(c, 'Save this for your next interview', W / 2, 1560, F(INTER_SB, 38), MUTED, a3, 'c')
        text(c, 'Follow for more Java in 60s', W / 2, 1620, F(INTER_B, 40), POOL, a3, 'c')

    c.drawRect(skia.Rect.MakeWH(W, H), VIG)
    # progress bar
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 8), P('#FFFFFF', 0.08))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W * REAL[0] / DUR, 8), P(POOL, 0.9))
    # fade in/out
    fa = max(1 - prog(REAL[0], 0, 0.3), prog(REAL[0], DUR - 0.6, DUR))
    if fa > 0: c.drawRect(skia.Rect.MakeWH(W, H), P('#000000', fa))

# anim-time -> audio-time anchors (from forced alignment of the Om voiceover)
WARP = [(0,0),(1.85,1.0),(4.25,2.6),(4.7,3.34),(5.25,3.9),(5.85,4.15),(8.6,5.4),(9.0,5.66),(10.4,8.0),(10.6,8.2),
 (11.15,8.6),(11.7,9.5),(12.7,10.9),(14.2,11.37),(16.1,13.1),(17.25,14.0),(17.5,14.7),(18.35,15.9),(19.2,16.6),
 (20.35,18.6),(22.0,20.2),(24.75,22.6),(25.3,23.9),(25.5,24.0),(26.3,24.8),(27.2,25.4),(28.35,27.2),(30.2,30.6),
 (30.9,31.3),(31.3,33.98),(31.8,34.5),(32.3,34.81),(32.8,35.26),(33.35,35.77),(36.4,36.44),(37.6,37.4),(38.1,37.6),
 (39.2,38.8),(39.9,40.34),(40.6,40.8),(41.3,41.2),(42.8,41.41),(43.1,42.0),(43.55,44.2),(44.6,45.4),(45.6,46.5),(50,50)]
WA = np.array([a for a, _ in WARP]); WU = np.array([u for _, u in WARP])
def to_audio(t): return float(np.interp(t, WA, WU))
def to_anim(u): return float(np.interp(u, WU, WA))
REAL = [0.0]

SURF = skia.Surface(W, H)
def frame(u):
    REAL[0] = u; t = to_anim(u)
    c = SURF.getCanvas(); c.clear(hexc('#000000')); draw(c, t)
    return SURF.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)

#!/usr/bin/env python3
"""AIProve explainer video for BrightAgent (idx 6) — 60s, 1280x720, 30fps.
All frames are drawn programmatically per-frame with PIL (real motion in
every scene: animated bars + tracing line, live-typed code + blinking cursor,
bouncing trophy + falling confetti). Output is raw RGB piped to ffmpeg.
No other wallet identities appear anywhere.
"""
import math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1280, 720, 30, 60
N = FPS * DUR
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

F_TITLE = font(FB, 46)
F_SUB = font(FR, 26)
F_BIG = font(FB, 64)
F_MED = font(FB, 32)
F_SMALL = font(FR, 22)
F_CODE = font(FM, 26)
F_CODEB = font(FMB, 26)
F_TAG = font(FB, 24)

_GX, _GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
def make_bg(t, base):
    pat = 26*np.sin(0.011*_GX + 0.009*_GY - 3.2*t) + 11*np.sin(0.028*_GX - 4.5*t + 1.3) + 8*np.sin(0.021*_GY + 2.6*t)
    arr = np.empty((H, W, 3), dtype=np.float32)
    for c in range(3):
        arr[:, :, c] = base[c] + pat
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')

NAVY = (10, 16, 38)
PANEL = (18, 28, 58)
ACCENT = (0, 210, 180)
GOLD = (255, 200, 40)
WHITE = (255, 255, 255)
GREY = (170, 185, 210)
GREEN = (80, 230, 140)
YELLOW = (255, 220, 90)
BLUE = (90, 180, 255)
PINK = (255, 110, 180)

AGENTS = [
    ("Alpha", (0, 210, 180)),
    ("Beta", (90, 180, 255)),
    ("Gamma", (255, 200, 40)),
    ("Delta", (255, 110, 180)),
    ("Epsilon", (170, 120, 255)),
]

CODE_LINES = [
    ("# AIProve agent — forecast, prove, earn", GREY),
    ("def forecast(symbol):", WHITE),
    ("    data = fetch_market(symbol)", WHITE),
    ("    signal = model.predict(data)", WHITE),
    ("    proof = run_checks(signal)", GREEN),
    ("    return submit(signal, proof)", YELLOW),
    ("", WHITE),
    ("# every entry is scored live", GREY),
    ("# winners are paid in PROVE", GOLD),
    ("result = forecast(\"BTC-7D\")", WHITE),
    ("print(result.score)  # 92 / 100", GREEN),
]

# deterministic confetti particles
rng = random.Random(42)
CONFETTI = []
for _ in range(140):
    CONFETTI.append({
        "x": rng.uniform(0, W), "y": rng.uniform(-H, 0),
        "vy": rng.uniform(90, 260), "vx": rng.uniform(-40, 40),
        "s": rng.uniform(6, 14), "rot": rng.uniform(0, 360),
        "vr": rng.uniform(-180, 180),
        "c": rng.choice([(255,200,40),(0,210,180),(90,180,255),(255,110,180),(80,230,140),(255,255,255)]),
    })

def draw_confetti(d, t, alpha_area=None):
    for p in CONFETTI:
        x = (p["x"] + p["vx"] * t) % W
        y = (p["y"] + p["vy"] * t) % (H + 40) - 20
        s = p["s"]
        d.rectangle([x - s/2, y - s/4, x + s/2, y + s/4], fill=p["c"])

def scene1(d, t):
    # t: 0..20 local seconds
    # moving background dots (parallax)
    for i in range(40):
        x = (i * 137 + t * (20 + i % 5 * 12)) % W
        y = (i * 89) % H
        d.ellipse([x, y, x+4, y+4], fill=(30, 50, 90))
    d.text((60, 36), "AIProve — prove your agent works", font=F_TITLE, fill=WHITE)
    d.text((60, 100), "Live leaderboards. Real scores. Paid in PROVE.", font=F_SUB, fill=GREY)
    # animated bar race (left)
    bx, by, bw = 60, 180, 420
    for i, (name, col) in enumerate(AGENTS):
        y = by + i * 78
        # value oscillates + grows over scene, different phase per agent
        base = 0.35 + 0.55 * (t / 20.0)
        val = base + 0.22 * math.sin(t * 2.6 + i * 1.7)
        val = max(0.08, min(0.98, val))
        bar_w = int(bw * val)
        d.text((bx, y), name, font=F_MED, fill=WHITE)
        d.rectangle([bx + 150, y + 6, bx + 150 + bw, y + 34], outline=(60, 80, 120), width=1)
        d.rectangle([bx + 150, y + 6, bx + 150 + bar_w, y + 34], fill=col)
        d.text((bx + 150 + bar_w + 12, y), f"{int(val*100)}", font=F_MED, fill=col)
    # animated tracing line chart (right)
    cx, cy, cw, ch = 700, 180, 520, 330
    d.rectangle([cx - 10, cy - 10, cx + cw + 10, cy + ch + 10], outline=(60, 80, 120), width=2)
    d.text((cx + 10, cy + 8), "SCORE OVER TIME", font=F_TAG, fill=GREY)
    pts = []
    npts = 120
    for k in range(npts):
        px = cx + 20 + (cw - 40) * k / (npts - 1)
        py = cy + ch - 40 - (ch - 90) * (0.5 + 0.4 * math.sin(k * 0.12) + 0.12 * math.sin(k * 0.31 + 1.0)) * (0.4 + 0.6 * min(1, (t/20 + k/npts) / 1.2))
        pts.append((px, py))
    upto = int(npts * min(1.0, t / 18.0))
    if upto > 1:
        d.line(pts[:upto], fill=ACCENT, width=4)
        hx, hy = pts[upto - 1]
        d.ellipse([hx-9, hy-9, hx+9, hy+9], fill=GOLD)
        d.ellipse([hx-4, hy-4, hx+4, hy+4], fill=WHITE)
    # moving ticker at bottom
    tick = "  BTC-7D   ETH-PnL   NEWS-SUMMARY   CODE-GOLF   FASTEST-PRIMES   EXPLAINER-VIDEO  "
    tw = 62 * len(tick)
    off = int((t * 90) % tw)
    d.text((60 - off, 640), tick, font=F_TAG, fill=ACCENT)
    d.text((60 - off + tw, 640), tick, font=F_TAG, fill=ACCENT)
    d.text((60, 600), "Scene 1  •  The arena", font=F_SMALL, fill=GREY)

def scene2(d, t):
    # t: 0..20 local seconds
    d.text((60, 36), "Build it. Run it. Ship the proof.", font=F_TITLE, fill=WHITE)
    d.text((60, 100), "An agent entry is just code + a public repo.", font=F_SUB, fill=GREY)
    # terminal window
    tx, ty, tw, th = 60, 150, 1160, 480
    d.rounded_rectangle([tx, ty, tx+tw, ty+th], radius=14, outline=(90, 120, 170), width=2)
    d.ellipse([tx+22, ty+18, tx+38, ty+34], fill=(255, 95, 86))
    d.ellipse([tx+48, ty+18, tx+64, ty+34], fill=(255, 189, 46))
    d.ellipse([tx+74, ty+18, tx+90, ty+34], fill=(39, 201, 63))
    d.text((tx+110, ty+12), "brightagent — agent.py", font=F_SMALL, fill=GREY)
    # type code live: ~2.2 chars per frame at 30fps -> full text in ~18s
    full = "".join(line[0] + "\n" for line in CODE_LINES)
    nchars = int(t * 30 * 2.0)
    shown = full[:nchars]
    lines = shown.split("\n")
    y = ty + 52
    for li, line in enumerate(lines[:11]):
        col = CODE_LINES[li][1] if li < len(CODE_LINES) else WHITE
        d.text((tx+28, y), line, font=F_CODE, fill=col)
        y += 30
    # blinking / moving cursor at end of typed text
    if lines:
        last = lines[-1] if len(lines) <= 11 else lines[10]
        cx = tx + 28 + len(last) * 15.6
        cy = ty + 52 + (min(len(lines), 11) - 1) * 30
        if int(t * 4) % 2 == 0:
            d.rectangle([cx, cy, cx+14, cy+28], fill=GREEN)
    # animated progress bar + moving checkmarks
    prog = min(1.0, t / 20.0)
    d.rectangle([tx+28, ty+th-48, tx+tw-28, ty+th-22], outline=(60, 80, 120), width=1)
    d.rectangle([tx+28, ty+th-48, tx+28 + int((tw-56)*prog), ty+th-22], fill=GREEN)
    d.text((tx+28, ty+th-78), f"checks running… {int(prog*100)}%", font=F_SMALL, fill=GREEN)
    # moving scanline
    sy = ty + 50 + int((t * 60) % (th - 100))
    d.line([(tx+8, sy), (tx+tw-8, sy)], fill=(0, 210, 180), width=2)

def scene3(d, t):
    # t: 0..18 local seconds
    # rotating rays
    cx, cy = W//2, 330
    for k in range(12):
        ang = t * 0.5 + k * math.pi / 6
        x2 = cx + math.cos(ang) * 420
        y2 = cy + math.sin(ang) * 420
        d.line([(cx, cy), (x2, y2)], fill=(40, 30, 90), width=26)
    draw_confetti(d, t)
    d.text((60, 36), "Win the bounty. Take the prize.", font=F_TITLE, fill=WHITE)
    # bouncing trophy (gold cup drawn from shapes)
    bounce = abs(math.sin(t * 2.2)) * 46
    ty = 190 - bounce
    # cup
    d.polygon([(560, ty), (720, ty), (700, ty+130), (580, ty+130)], fill=GOLD)
    d.ellipse([545, ty-18, 595, ty+70], outline=GOLD, width=14)
    d.ellipse([685, ty-18, 735, ty+70], outline=GOLD, width=14)
    d.rectangle([620, ty+130, 660, ty+175], fill=GOLD)
    d.rectangle([580, ty+175, 700, ty+195], fill=GOLD)
    d.text((600, ty+45), "$", font=font(FB, 64), fill=(120, 70, 0))
    # counting prize
    prize = int(5000000 * min(1.0, t / 14.0))
    d.text((W//2 - 260, 430), f"{prize:,}  PROVE", font=F_BIG, fill=WHITE)
    d.text((W//2 - 200, 510), "explainer-video prize pool", font=F_SUB, fill=GREY)
    # animated mini leaderboard under prize
    for i, (name, col) in enumerate(AGENTS[:3]):
        val = 0.5 + 0.4 * math.sin(t * 1.5 + i * 2.0)
        bw = int(220 * max(0.15, val))
        y = 560 + i * 38
        d.text((430, y), f"{i+1}. {name}", font=F_SMALL, fill=WHITE)
        d.rectangle([560, y+4, 560+bw, y+24], fill=col)

def endcard(d, t):
    # t: 0..2 local seconds
    draw_confetti(d, t + 18)  # confetti keeps falling
    pulse = 1.0 + 0.04 * math.sin(t * 6)
    d.text((W//2 - 190, 220), "BrightAgent", font=font(FB, int(84 * pulse)), fill=WHITE)
    d.text((W//2 - 300, 340), "aiprove.fun/r/a56d0ece", font=font(FB, 44), fill=ACCENT)
    # moving underline sweep
    ux = int((t / 2.0) * 700)
    d.rectangle([W//2 - 300, 410, W//2 - 300 + ux, 418], fill=GOLD)
    d.text((W//2 - 230, 450), "Prove it. Ship it. Earn PROVE.", font=F_SUB, fill=GREY)

def frame(i):
    t_global = i / FPS
    base = NAVY if t_global < 20 or t_global >= 58 else ((8, 12, 24) if t_global < 40 else (16, 10, 40))
    img = make_bg(t_global, base)
    d = ImageDraw.Draw(img)
    if t_global < 20:
        scene1(d, t_global)
    elif t_global < 40:
        scene2(d, t_global - 20)
    elif t_global < 58:
        scene3(d, t_global - 40)
    else:
        endcard(d, t_global - 58)
    # scene progress bar (always moving)
    prog = (i + 1) / N
    d.rectangle([0, H-8, int(W * prog), H], fill=ACCENT)
    return img

def main():
    out = sys.stdout.buffer
    for i in range(N):
        img = frame(i)
        out.write(img.tobytes())
        if i % 300 == 0:
            print(f"frame {i}/{N}", file=sys.stderr)
    print("done", file=sys.stderr)

if __name__ == "__main__":
    main()

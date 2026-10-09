"""EarlyLoot thumbnail style v2 (YouTube-gaming style), 1280x720.
Energetic background (theme gradient + light rays + glow + speed lines + halftone),
a cut-out character/prop with rim light on one side, and stacked huge text:
small game-name label (plain bold text, never an official logo), white line(s) and one huge
yellow key word, heavy black outline, drop shadow, slight tilt.

Front matter example:
thumb:
  style: v2
  label: "GTA VI"                 # game name as plain text
  lines: ["RADIO", "REVEALED"]    # 2-4 words total, top to bottom
  key: 0                          # index of the huge yellow line
  theme: fire                     # fire | volt | neon | ice
  character: prop-boombox.png     # file in media/characters/ (transparent PNG)
  side: right                     # character side: left | right
  badge: "NEW"                    # optional corner badge
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F_KEY = os.path.join(ROOT, 'static/fonts/Anton-Regular.ttf')
F_BOLD = os.path.join(ROOT, 'static/fonts/ArchivoBlack-Regular.ttf')
W, H = 1280, 720
YEL, WHITE, BLACK = (255, 214, 10), (255, 255, 255), (0, 0, 0)
THEMES = {  # dark, mid, light (glow), rays
    'fire': ((70, 0, 0), (215, 30, 10), (255, 170, 40), (255, 120, 30)),
    'volt': ((60, 50, 0), (225, 190, 0), (255, 250, 150), (255, 240, 90)),
    'neon': ((40, 0, 50), (220, 30, 120), (255, 150, 60), (255, 90, 160)),
    'ice':  ((0, 20, 60), (0, 120, 220), (170, 240, 255), (120, 220, 255)),
}

def _radial(size, center, inner, outer, radius):
    w, h = size; g = Image.new('L', (w, h)); px = g.load()
    cx, cy = center
    small = Image.new('L', (w // 8, h // 8)); sp = small.load()
    for y in range(h // 8):
        for x in range(w // 8):
            d = math.hypot(x * 8 - cx, y * 8 - cy) / radius
            sp[x, y] = int(255 * max(0.0, 1 - d))
    g = small.resize((w, h), Image.BILINEAR)
    return Image.composite(Image.new('RGB', size, inner), Image.new('RGB', size, outer), g)

def background(theme, focus, bg_image=None):
    dark, mid, light, ray = THEMES.get(theme, THEMES['fire'])
    im = _radial((W, H), focus, mid, dark, 900).convert('RGBA')
    if bg_image and os.path.exists(bg_image):  # faint, color-graded scene underneath
        sc = Image.open(bg_image).convert('L').resize((W, H)).filter(ImageFilter.GaussianBlur(3))
        sc = Image.merge('RGBA', [sc.point(lambda v: int(v * mid[0] / 255)), sc.point(lambda v: int(v * mid[1] / 255)),
                                  sc.point(lambda v: int(v * mid[2] / 255)), Image.new('L', (W, H), 70)])
        im.alpha_composite(sc)
    # light rays
    rays = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(rays); n = 22; R = 2000
    for i in range(n):
        a0 = 2 * math.pi * i / n; a1 = a0 + math.pi / n * 0.55
        d.polygon([focus, (focus[0] + R * math.cos(a0), focus[1] + R * math.sin(a0)),
                   (focus[0] + R * math.cos(a1), focus[1] + R * math.sin(a1))], fill=ray + (55,))
    im.alpha_composite(rays.filter(ImageFilter.GaussianBlur(2)))
    # central glow
    glow = Image.new('RGBA', (W, H)); ImageDraw.Draw(glow).ellipse((focus[0] - 330, focus[1] - 330, focus[0] + 330, focus[1] + 330), fill=light + (150,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    # speed lines
    rnd = random.Random(7); sl = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(sl)
    for _ in range(26):
        y = rnd.randint(0, H); x = rnd.randint(-200, W); L = rnd.randint(150, 420)
        d.line((x, y, x + L, y - L * 0.35), fill=(255, 255, 255, rnd.randint(40, 110)), width=rnd.randint(2, 5))
    im.alpha_composite(sl)
    # halftone dots (corner opposite focus)
    ht = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(ht)
    ox = 0 if focus[0] > W / 2 else W
    for y in range(0, 300, 22):
        for x in range(0, 380, 22):
            r = max(0, 9 - (x + y) / 60)
            px = ox + x if ox == 0 else ox - x
            if r > 0.6: d.ellipse((px - r, H - y - r, px + r, H - y + r), fill=(0, 0, 0, 90))
    im.alpha_composite(ht)
    return im

def place_character(im, path, side, light, max_h=700, max_w=700):
    ch = Image.open(path).convert('RGBA'); ch = ch.crop(ch.getbbox())
    bottom = ch.split()[3].crop((0, ch.height - 2, ch.width, ch.height))
    cut_at_bottom = sum(1 for v in bottom.getdata() if v > 128) > ch.width * 0.2  # figure cut off at waist/legs
    if cut_at_bottom: max_w = max(max_w, 800)
    s = min(max_h / ch.height, max_w / ch.width); ch = ch.resize((int(ch.width * s), int(ch.height * s)), Image.LANCZOS)
    ch = ImageEnhance.Contrast(ch).enhance(1.12)
    x = (30 if side == 'left' else W - ch.width - 30) if not cut_at_bottom else (-60 if side == 'left' else W - ch.width + 60)
    y = H - ch.height + (10 if ch.height > 500 else -40)
    if cut_at_bottom: y = H - ch.height + 4
    elif ch.height <= 500: y = (H - ch.height) // 2 + 60
    a = ch.split()[3]
    # dark outer shadow, then colored rim glow, then the character
    sh = Image.new('RGBA', ch.size, (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(14)))
    rim = Image.new('RGBA', ch.size, light + (0,)); rim.putalpha(a.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(8)))
    pad = 40; layer = Image.new('RGBA', (W, H))
    layer.alpha_composite(sh, (x + 12, y + 12)); [layer.alpha_composite(rim, (x, y)) for _ in range(3)]
    layer.alpha_composite(ch, (x, y))
    im.alpha_composite(layer)
    return x, ch.width

def _text_img(txt, font, fill, stroke):
    b = font.getbbox(txt, stroke_width=stroke); w, h = b[2] - b[0] + 40, b[3] - b[1] + 40
    L = Image.new('RGBA', (w, h)); off = (20 - b[0], 20 - b[1])
    sh = Image.new('RGBA', (w, h)); ImageDraw.Draw(sh).text((off[0] + 10, off[1] + 12), txt, font=font, fill=(0, 0, 0, 220), stroke_width=stroke, stroke_fill=(0, 0, 0, 220))
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(L).text(off, txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=BLACK)
    return L

def _fit(path, txt, size, maxw, stroke):
    while size > 40:
        f = ImageFont.truetype(path, size)
        b = f.getbbox(txt, stroke_width=stroke)
        if b[2] - b[0] <= maxw: return f
        size -= 4
    return ImageFont.truetype(path, size)

def render(out, lines, key=0, label=None, theme='fire', character=None, side='right', badge=None, bg_image=None):
    focus = (W - 330, 330) if side == 'right' else (330, 330)
    im = background(theme, focus, bg_image)
    light = THEMES.get(theme, THEMES['fire'])[2]
    if character:
        p = character if os.path.isabs(character) else os.path.join(ROOT, 'media/characters', character)
        place_character(im, p, side, light)
    # text block
    maxw = 690
    block = []
    if label: block.append(_text_img(label.upper(), _fit(F_BOLD, label.upper(), 64, 420, 8), WHITE, 8))
    for i, t in enumerate(lines):
        t = t.upper()
        if i == key: block.append(_text_img(t, _fit(F_KEY, t, 230, maxw, 12), YEL, 12))
        else: block.append(_text_img(t, _fit(F_BOLD, t, 110, maxw, 10), WHITE, 10))
    gap = -26; bw = max(b.width for b in block); bh = sum(b.height for b in block) + gap * (len(block) - 1)
    T = Image.new('RGBA', (bw, bh)); y = 0
    for b in block:
        T.alpha_composite(b, ((bw - b.width) // 2, y)); y += b.height + gap
    T = T.rotate(4, expand=True, resample=Image.BICUBIC)
    if T.height > H - 30: T = T.resize((int(T.width * (H - 30) / T.height), H - 30), Image.LANCZOS)
    cx = (W * 0.33) if side == 'right' else (W * 0.67)
    tx = int(max(10, min(W - T.width - 10, cx - T.width / 2))); ty = (H - T.height) // 2
    im.alpha_composite(T, (tx, ty))
    if badge:
        d = ImageDraw.Draw(im); bf = ImageFont.truetype(F_KEY, 46); bwid = bf.getbbox(badge.upper())[2] + 44
        bx = 34 if side == 'right' else W - bwid - 34
        d.rounded_rectangle((bx, 30, bx + bwid, 100), 12, fill=YEL, outline=BLACK, width=5); d.text((bx + 22, 36), badge.upper(), font=bf, fill=BLACK)
    # vignette
    v = Image.new('L', (W, H), 0); ImageDraw.Draw(v).rectangle((0, 0, W, H), outline=255, width=60)
    im.alpha_composite(Image.merge('RGBA', [Image.new('L', (W, H), 0)] * 3 + [v.filter(ImageFilter.GaussianBlur(50)).point(lambda p: int(p * .55))]))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.convert('RGB').save(out, quality=88, optimize=True, progressive=True)
    return out

if __name__ == '__main__':  # quick demo set
    o = os.path.join(ROOT, 'preview')
    render(f'{o}/v2-demo-gta.jpg', ['GTA VI', 'RADIO', 'REVEALED'][1:], key=0, label='GTA VI', theme='neon', character='prop-boombox.png', side='right', badge='NEW')
    render(f'{o}/v2-demo-mw4.jpg', ['SOLO', 'PLAYER'], key=0, label='MW4', theme='fire', character='mw4-operator.png', side='left')
    render(f'{o}/v2-demo-arc.jpg', ['FROZEN', 'TRAIL LIVE'], key=0, label='ARC RAIDERS', theme='ice', character='arc-raider.png', side='right')
    print('ok')

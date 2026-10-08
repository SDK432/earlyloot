"""Thumbnail renderer (YouTube-style overlay text on a background screenshot).
Backgrounds: media/screenshots/<game>/*.jpg|png|webp. Real screenshots are preferred over
placeholder-*.jpg; when several exist, each article gets one picked deterministically from its slug
(or set `image:` in the article front matter to force a file)."""
import glob, os, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT=os.path.join(ROOT,'static/fonts/Anton-Regular.ttf')
W,H=1280,720
COLORS={'yellow':(255,214,10),'green':(124,255,58),'white':(255,255,255)}
EXT=('.jpg','.jpeg','.png','.webp')

def pick_bg(game,slug,image=None):
    if image:
        p=image if os.path.isabs(image) else os.path.join(ROOT,'media/screenshots',game,image)
        if os.path.exists(p): return p
    files=sorted(f for f in glob.glob(f'{ROOT}/media/screenshots/{game}/*') if f.lower().endswith(EXT))
    real=[f for f in files if not os.path.basename(f).startswith('placeholder')]
    pool=real or files
    if not pool: raise SystemExit(f'No background image for {game}: add one to media/screenshots/{game}/')
    return pool[int(hashlib.md5(slug.encode()).hexdigest(),16)%len(pool)]

def _bg(path):
    im=Image.open(path).convert('RGB'); r=max(W/im.width,H/im.height)
    im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2; im=im.crop((x,y,x+W,y+H))
    return ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.25)).enhance(1.1)

def _fit(txt,size,maxw):
    while size>60:
        f=ImageFont.truetype(FONT,size)
        if f.getbbox(txt)[2]+20<=maxw: return f
        size-=6
    return ImageFont.truetype(FONT,size)

def _text(txt,font,fill,tilt):
    b=font.getbbox(txt); w,h=b[2]+60,b[3]+60
    L=Image.new('RGBA',(w,h)); sh=Image.new('RGBA',(w,h))
    ImageDraw.Draw(sh).text((38,40),txt,font=font,fill=(0,0,0,230),stroke_width=14,stroke_fill=(0,0,0,230))
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(L).text((30,26),txt,font=font,fill=fill,stroke_width=10,stroke_fill=(0,0,0))
    return L.rotate(tilt,expand=True,resample=Image.BICUBIC)

def render(out,game,slug,line1,line2,accent='yellow',badge=None,image=None):
    acc=COLORS.get(accent,COLORS['yellow'])
    im=_bg(pick_bg(game,slug,image)).convert('RGBA')
    g=Image.new('RGBA',(W,H)); gd=ImageDraw.Draw(g)
    for x in range(W): gd.line([(x,0),(x,H)],fill=(0,0,0,int(175*max(0,(x-W*0.3)/(W*0.7)))))
    im.alpha_composite(g)
    a=_text(line1.upper(),_fit(line1.upper(),150,760),COLORS['white'],4)
    b=_text(line2.upper(),_fit(line2.upper(),170,780),acc,4)
    top=max(130,(H-(a.height+b.height-70))//2)
    im.alpha_composite(a,(W-a.width-30,top)); im.alpha_composite(b,(W-b.width-20,top+a.height-70))
    if badge:
        d=ImageDraw.Draw(im); bf=ImageFont.truetype(FONT,48); bw=bf.getbbox(badge.upper())[2]+50
        d.rounded_rectangle((40,40,40+bw,115),14,fill=acc,outline=(0,0,0),width=5)
        d.text((65,46),badge.upper(),font=bf,fill=(0,0,0))
    os.makedirs(os.path.dirname(out),exist_ok=True)
    im.convert('RGB').save(out,quality=86,optimize=True,progressive=True)
    return out

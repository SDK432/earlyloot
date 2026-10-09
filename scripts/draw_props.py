#!/usr/bin/env python3
"""Draw original vector 'props' (no IP) as transparent PNG cut-outs for thumbnails.
Usage: python3 scripts/draw_props.py   -> media/characters/prop-boombox.png"""
import os
from PIL import Image, ImageDraw, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 3  # supersample

def boombox(path):
    W, H = 900 * S, 700 * S
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    # handle + antenna
    d.rounded_rectangle((260*S, 60*S, 640*S, 200*S), 50*S, outline=(25, 25, 30), width=34*S)
    d.line((700*S, 230*S, 840*S, 20*S), fill=(200, 200, 210), width=10*S)
    d.ellipse((828*S, 8*S, 852*S, 32*S), fill=(230, 230, 240))
    # body
    d.rounded_rectangle((40*S, 180*S, 860*S, 660*S), 60*S, fill=(30, 30, 38), outline=(10, 10, 12), width=12*S)
    d.rounded_rectangle((60*S, 200*S, 840*S, 280*S), 30*S, fill=(220, 40, 120))  # top stripe (pink)
    for i, c in enumerate([(255, 214, 10), (124, 255, 58), (0, 220, 255)]):
        d.rounded_rectangle(((90 + i*70)*S, 222*S, (140 + i*70)*S, 258*S), 10*S, fill=c)
    # cassette window
    d.rounded_rectangle((330*S, 300*S, 570*S, 430*S), 18*S, fill=(15, 15, 20), outline=(255, 214, 10), width=6*S)
    for cx in (395, 505):
        d.ellipse(((cx-30)*S, 335*S, (cx+30)*S, 395*S), fill=(60, 60, 70), outline=(230, 230, 230), width=5*S)
        d.ellipse(((cx-10)*S, 355*S, (cx+10)*S, 375*S), fill=(15, 15, 20))
    # dial/equalizer
    for i in range(9):
        h = [40, 70, 55, 90, 60, 80, 45, 65, 35][i]
        d.rectangle(((350 + i*24)*S, (620 - h)*S, (364 + i*24)*S, 620*S), fill=(124, 255, 58) if i % 2 else (255, 214, 10))
    # speakers
    for cx in (185, 715):
        cy = 470
        for r, col in [(150, (12, 12, 15)), (140, (55, 55, 65)), (110, (20, 20, 24)), (70, (75, 75, 88)), (34, (230, 40, 120)), (14, (255, 214, 10))]:
            d.ellipse(((cx-r)*S, (cy-r)*S, (cx+r)*S, (cy+r)*S), fill=col)
        # shine
        d.arc(((cx-120)*S, (cy-120)*S, (cx+120)*S, (cy+120)*S), 200, 250, fill=(160, 160, 175), width=8*S)
    # body highlight
    hl = Image.new('RGBA', (W, H)); ImageDraw.Draw(hl).rounded_rectangle((60*S, 290*S, 840*S, 320*S), 15*S, fill=(255, 255, 255, 25))
    im.alpha_composite(hl)
    im = im.resize((W // S, H // S), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path)
    return path

if __name__ == '__main__':
    print(boombox(os.path.join(ROOT, 'media/characters/prop-boombox.png')))

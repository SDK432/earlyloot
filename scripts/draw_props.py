#!/usr/bin/env python3
"""Draw original vector 'props' (no IP) as transparent PNG cut-outs for thumbnails.
Usage: python3 scripts/draw_props.py   -> media/characters/prop-boombox.png
       python3 scripts/draw_props.py helicopter -> media/characters/prop-helicopter.png"""
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

def helicopter(path):
    """Generic police-style helicopter with searchlight beam (no text, no markings)."""
    W, H = 900 * S, 1100 * S
    im = Image.new('RGBA', (W, H))
    # searchlight beam (soft, behind the body)
    beam = Image.new('RGBA', (W, H)); bd = ImageDraw.Draw(beam)
    bd.polygon([(430*S, 400*S), (470*S, 410*S), (800*S, 1100*S), (100*S, 1100*S)], fill=(255, 245, 200, 120))
    beam = beam.filter(ImageFilter.GaussianBlur(18*S)); im.alpha_composite(beam)
    d = ImageDraw.Draw(im)
    body, dark, stripe = (28, 36, 58), (12, 14, 22), (235, 238, 245)
    # tail boom + fin + tail rotor
    d.polygon([(560*S, 250*S), (800*S, 232*S), (805*S, 262*S), (560*S, 320*S)], fill=body, outline=dark)
    d.polygon([(770*S, 237*S), (830*S, 147*S), (855*S, 152*S), (815*S, 262*S)], fill=body, outline=dark)
    d.ellipse((780*S, 157*S, 890*S, 267*S), outline=(150, 155, 170), width=6*S)
    d.line((835*S, 157*S, 835*S, 267*S), fill=(190, 195, 205), width=8*S)
    # main fuselage
    d.ellipse((150*S, 170*S, 640*S, 400*S), fill=body, outline=dark, width=8*S)
    d.polygon([(560*S, 210*S), (640*S, 250*S), (600*S, 360*S), (520*S, 380*S)], fill=body)
    # white side stripe
    d.polygon([(175*S, 300*S), (630*S, 270*S), (625*S, 292*S), (185*S, 325*S)], fill=stripe)
    # cockpit glass
    d.chord((150*S, 175*S, 420*S, 395*S), 120, 250, fill=(70, 150, 200), outline=dark, width=6*S)
    d.chord((175*S, 195*S, 395*S, 375*S), 140, 210, fill=(170, 225, 250))
    # side window + door line
    d.rounded_rectangle((350*S, 210*S, 470*S, 280*S), 18*S, fill=(70, 150, 200), outline=dark, width=5*S)
    d.line((480*S, 200*S, 480*S, 380*S), fill=dark, width=5*S)
    # searchlight pod
    d.ellipse((410*S, 380*S, 490*S, 425*S), fill=(60, 60, 70), outline=dark, width=4*S)
    d.ellipse((428*S, 395*S, 472*S, 425*S), fill=(255, 250, 220))
    # skids
    for x in (250, 500):
        d.line((x*S, 390*S, (x-20)*S, 460*S), fill=dark, width=14*S)
    d.rounded_rectangle((150*S, 455*S, 620*S, 475*S), 10*S, fill=dark)
    # rotor mast + blurred main rotor
    d.rectangle((370*S, 130*S, 400*S, 180*S), fill=dark)
    d.rounded_rectangle((300*S, 150*S, 480*S, 185*S), 14*S, fill=body, outline=dark, width=5*S)
    rot = Image.new('RGBA', (W, H)); rd = ImageDraw.Draw(rot)
    rd.ellipse((-20*S, 95*S, 790*S, 165*S), fill=(200, 205, 215, 70))
    rd.polygon([(0*S, 118*S), (385*S, 128*S), (770*S, 140*S), (385*S, 140*S)], fill=(25, 25, 30, 230))
    rot = rot.filter(ImageFilter.GaussianBlur(3*S)); im.alpha_composite(rot)
    d = ImageDraw.Draw(im)
    d.ellipse((365*S, 115*S, 405*S, 150*S), fill=dark)
    # red / blue beacons with glow
    glow = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(glow)
    for (x, y, c) in [(330, 190, (255, 40, 60)), (450, 190, (40, 120, 255)), (800, 229, (255, 40, 60))]:
        gd.ellipse(((x-40)*S, (y-40)*S, (x+40)*S, (y+40)*S), fill=c + (150,))
    glow = glow.filter(ImageFilter.GaussianBlur(16*S)); im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    for (x, y, c) in [(330, 190, (255, 90, 100)), (450, 190, (110, 170, 255)), (800, 229, (255, 90, 100))]:
        d.ellipse(((x-11)*S, (y-11)*S, (x+11)*S, (y+11)*S), fill=c)
    # rim highlight on top of fuselage
    hl = Image.new('RGBA', (W, H)); ImageDraw.Draw(hl).arc((165*S, 180*S, 630*S, 390*S), 200, 320, fill=(255, 200, 150, 120), width=8*S)
    im.alpha_composite(hl)
    im = im.resize((W // S, H // S), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path)
    return path

if __name__ == '__main__':
    import sys
    if 'helicopter' in sys.argv[1:]:
        print(helicopter(os.path.join(ROOT, 'media/characters/prop-helicopter.png')))
    else:
        print(boombox(os.path.join(ROOT, 'media/characters/prop-boombox.png')))

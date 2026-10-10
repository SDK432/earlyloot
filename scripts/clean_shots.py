#!/usr/bin/env python3
"""Clean Rick's ARC Raiders gameplay screenshots (2560x1440) for thumbnails:
inpaint small HUD bits, crop 16:9 away from HUD edges/corners, save 1600x900 JPG q85.
Coordinates below are in 1024x576 preview space (x2.5 = full res).
Usage: python3 scripts/clean_shots.py   (raw PNGs are gitignored; clean JPGs are committed)"""
import os, cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'media/screenshots/arc-raiders')
S = 2.5
# HUD rects present on every shot (inpainted anyway as a safety net)
COMMON = [(375, 0, 665, 72), (10, 500, 175, 555), (930, 410, 1015, 465), (812, 465, 1015, 555),
          (915, 555, 1024, 576), (978, 160, 1010, 192), (505, 282, 520, 296)]
EXTRA = {2: [(608, 332, 628, 352)], 3: [(450, 508, 575, 530)],
         5: [(568, 300, 648, 324), (703, 243, 723, 263)]}
TOP, BOT = 78, 500                        # crop rows (preview space) -> 422 tall
X0 = {1: 0, 2: 0, 3: 0, 4: 0, 5: 172, 6: 172}  # crop left edge per shot (centres the raider)

def run():
    os.makedirs(os.path.join(D, 'clean'), exist_ok=True)
    for i in range(1, 7):
        src = os.path.join(D, f'rick-arc-0{i}.png')
        if not os.path.exists(src): continue
        im = cv2.imread(src)
        h, w = im.shape[:2]; s = w / 1024
        mask = np.zeros((h, w), np.uint8)
        for x0, y0, x1, y1 in COMMON + EXTRA.get(i, []):
            cv2.rectangle(mask, (int(x0 * s), int(y0 * s)), (int(x1 * s), int(y1 * s)), 255, -1)
        im = cv2.inpaint(im, mask, 9, cv2.INPAINT_TELEA)
        ch = (BOT - TOP); cw = ch * 16 / 9
        x0 = X0[i]; crop = im[int(TOP * s):int(BOT * s), int(x0 * s):int((x0 + cw) * s)]
        crop = cv2.resize(crop, (1600, 900), interpolation=cv2.INTER_AREA)
        out = os.path.join(D, 'clean', f'arc-0{i}.jpg')
        cv2.imwrite(out, crop, [cv2.IMWRITE_JPEG_QUALITY, 85, cv2.IMWRITE_JPEG_OPTIMIZE, 1, cv2.IMWRITE_JPEG_PROGRESSIVE, 1])
        print(out, os.path.getsize(out) // 1024, 'KB')

if __name__ == '__main__': run()

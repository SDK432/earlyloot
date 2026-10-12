#!/usr/bin/env python3
"""Cut out operators from Rick's MW4/Warzone lobby screenshots -> media/characters/mw4-rick-0N.png
(region between the lobby menus only, so no UI ends up in the cut-out). Usage: python3 scripts/cutout_mw4.py"""
import os, cv2, numpy as np
from PIL import Image
from rembg import remove, new_session
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'media/screenshots/mw4-warzone')
REGION = (730, 185, 1900, 1320)                       # x0, y0, x1, y1 in the 2560x1440 lobby shot
FIX = [(690, 930, 800, 1075), (1785, 180, 1905, 345)]  # debug text, party panel/speaker icon corner
CUTS = {1: 5, 2: 7, 3: 2, 4: 12, 5: 18, 6: 9, 7: 11, 8: 14}   # out N: raw shot

def largest(alpha):
    _, bw = cv2.threshold(alpha, 30, 255, cv2.THRESH_BINARY)
    n, lab, st, _ = cv2.connectedComponentsWithStats(bw)
    if n <= 1: return alpha
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); keep = (lab == k).astype(np.uint8) * 255
    # fill small enclosed holes only (components of the background that don't touch the border)
    inv = cv2.bitwise_not(keep); h, w = keep.shape
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv)
    holes = np.zeros_like(keep)
    for i in range(1, n2):
        x, y, bw_, bh_, area = st2[i]
        if x > 0 and y > 0 and x + bw_ < w and y + bh_ < h and area < 0.01 * h * w: holes[lab2 == i] = 255
    return np.where(keep > 0, np.maximum(alpha, (holes > 0) * 255), 0).astype(np.uint8)

if __name__ == '__main__':
    s = new_session('isnet-general-use')
    for n, raw in CUTS.items():
        im = cv2.imread(os.path.join(D, f'rick-mw4-{raw:02d}.png'))
        mask = np.zeros(im.shape[:2], np.uint8)
        for r in FIX: cv2.rectangle(mask, r[:2], r[2:], 255, -1)
        im = cv2.inpaint(im, mask, 9, cv2.INPAINT_TELEA)
        x0, y0, x1, y1 = REGION
        pil = Image.fromarray(cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2RGB))
        out = remove(pil, session=s)
        a = largest(np.array(out.split()[3])); out.putalpha(Image.fromarray(a))
        out = out.crop(out.getbbox())
        p = os.path.join(ROOT, 'media/characters', f'mw4-rick-{n:02d}.png'); out.save(p, optimize=True)
        print(p, out.size, os.path.getsize(p) // 1024, 'KB')

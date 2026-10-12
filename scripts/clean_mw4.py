#!/usr/bin/env python3
"""Clean Rick's MW4/Warzone screenshots (2560x1440) for thumbnails.
Per shot: inpaint leftover HUD bits (full-res rects; 'sat' rects only mask coloured/bright text pixels),
crop 16:9 away from all menus/HUD, save 1600x900 JPG q85 to media/screenshots/mw4-warzone/clean/mw4-NN.jpg.
Raw PNGs (rick-mw4-NN.png) are gitignored. Usage: python3 scripts/clean_mw4.py"""
import os, cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'media/screenshots/mw4-warzone')
LOBBY_FIX = [(690, 930, 800, 1075), (1785, 280, 1832, 335)]  # + party speaker icon          # tiny build/debug text left of the operator in lobby shots
# out#: (raw#, (x0, y0, width), inpaint rects, sat-masked rects)
SHOTS = {
    1:  (2,  (740, 185, 1090), LOBBY_FIX, []),
    2:  (4,  (740, 185, 1090), LOBBY_FIX, []),
    3:  (5,  (740, 185, 1090), LOBBY_FIX, []),
    4:  (7,  (740, 185, 1090), LOBBY_FIX, []),
    5:  (9,  (740, 185, 1090), LOBBY_FIX, []),
    6:  (11, (740, 185, 1090), LOBBY_FIX, []),
    7:  (12, (740, 185, 1090), LOBBY_FIX, []),
    8:  (13, (740, 185, 1090), LOBBY_FIX, []),
    9:  (14, (740, 185, 1090), LOBBY_FIX, []),
    10: (18, (740, 185, 1090), LOBBY_FIX, []),
    11: (1,  (420, 0, 2133), [], []),
    12: (15, (470, 215, 1380), [(1195, 210, 1355, 350)], []),
    13: (16, (440, 330, 1600), [], []),
    14: (19, (440, 330, 1600), [], []),
    15: (21, (400, 170, 1760), [(1225, 488, 1330, 522)], []),
    16: (20, (570, 325, 1387), [], [(890, 500, 1055, 565), (1020, 585, 1230, 630), (745, 635, 980, 715),
                                    (1420, 685, 1605, 730), (1730, 565, 1895, 605), (1235, 395, 1380, 450),
                                    (1600, 390, 1850, 425), (1520, 435, 1705, 475), (1730, 435, 1945, 505),
                                    (1190, 640, 1385, 690)]),
}
# skipped raws: 03 (near-duplicate of 04), 06 (near-duplicate of 05), 08 (face sits under the top nav bar),
# 10 (near-duplicate of 09), 17 (near-duplicate of 16), 22 (waypoint/revive/prompt overlays across the centre),
# 23 (menu-covered, dark duplicate of 01)

def rect_mask(mask, r):
    cv2.rectangle(mask, (r[0], r[1]), (r[2], r[3]), 255, -1)

def run(only=None):
    os.makedirs(os.path.join(D, 'clean'), exist_ok=True)
    for n, (raw, (x0, y0, cw), rects, sats) in SHOTS.items():
        if only and n not in only: continue
        src = os.path.join(D, f'rick-mw4-{raw:02d}.png')
        if not os.path.exists(src): continue
        im = cv2.imread(src); h, w = im.shape[:2]
        mask = np.zeros((h, w), np.uint8)
        for r in rects: rect_mask(mask, r)
        if sats:
            hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
            for x_0, y_0, x_1, y_1 in sats:
                sub = hsv[y_0:y_1, x_0:x_1]
                m = ((sub[..., 1] > 60) & (sub[..., 2] > 110)) | (sub[..., 2] > 200)
                mask[y_0:y_1, x_0:x_1] |= (m.astype(np.uint8) * 255)
        if mask.any():
            mask = cv2.dilate(mask, np.ones((9, 9), np.uint8))
            im = cv2.inpaint(im, mask, 11, cv2.INPAINT_TELEA)
        ch = round(cw * 9 / 16)
        crop = im[y0:y0 + ch, x0:x0 + cw]
        crop = cv2.resize(crop, (1600, 900), interpolation=cv2.INTER_AREA if cw >= 1600 else cv2.INTER_LANCZOS4)
        out = os.path.join(D, 'clean', f'mw4-{n:02d}.jpg')
        cv2.imwrite(out, crop, [cv2.IMWRITE_JPEG_QUALITY, 85, cv2.IMWRITE_JPEG_OPTIMIZE, 1, cv2.IMWRITE_JPEG_PROGRESSIVE, 1])
        print(out, f'(raw {raw:02d})', os.path.getsize(out) // 1024, 'KB')

if __name__ == '__main__': run()

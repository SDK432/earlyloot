#!/usr/bin/env python3
"""Rotation of Rick's MW4/Warzone thumbnail images (cut-outs + clean scenes), tracked in content/mw4-image-usage.json.
  python3 scripts/mw4_images.py next            -> suggests the least-recently-used character + background pair
                                                  (never the previous post's images, never a cut-out on its own source shot)
  python3 scripts/mw4_images.py use <slug> <character.png> <bg.jpg>   -> records the pair (run after writing the post)
  python3 scripts/mw4_images.py list            -> usage history"""
import os, sys, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, 'content/mw4-image-usage.json')
CHARS = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, 'media/characters/mw4-rick-*.png')))
BGS = sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, 'media/screenshots/mw4-warzone/clean/mw4-*.jpg')))
# cut-out -> the clean scene made from the same raw shot (don't pair them)
SOURCE = {'mw4-rick-01.png': 'mw4-03.jpg', 'mw4-rick-02.png': 'mw4-04.jpg', 'mw4-rick-03.png': 'mw4-01.jpg',
          'mw4-rick-04.png': 'mw4-07.jpg', 'mw4-rick-05.png': 'mw4-10.jpg', 'mw4-rick-06.png': 'mw4-05.jpg',
          'mw4-rick-07.png': 'mw4-06.jpg', 'mw4-rick-08.png': 'mw4-09.jpg'}
# in-match scenes (11-16) read best as full backgrounds behind a cut-out; lobby scenes (01-10) work as solo full-bleed bgs
SCENES = [b for b in BGS if int(b[-6:-4]) >= 11]

def load(): return json.load(open(LOG)) if os.path.exists(LOG) else []

def lru(items, used):
    last = {x: i for i, x in enumerate(used)}
    return sorted(items, key=lambda x: last.get(x, -1))

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'next'; log = load()
    if cmd == 'use':
        slug, ch, bg = sys.argv[2:5]
        log = [e for e in log if e['slug'] != slug] + [{'slug': slug, 'character': ch, 'bg': bg}]
        json.dump(log, open(LOG, 'w'), indent=1); print('recorded', slug)
    elif cmd == 'list':
        for e in log: print(e['slug'], e['character'], e['bg'])
    else:
        prev = log[-1] if log else {}
        ch = next(c for c in lru(CHARS, [e['character'] for e in log]) if c != prev.get('character'))
        bg = next(b for b in lru(SCENES, [e['bg'] for e in log])
                  if b != prev.get('bg') and not b.endswith(SOURCE.get(ch, '-')))
        print(f'character: {ch}\nbg: {bg}')

if __name__ == '__main__': main()

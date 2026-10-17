#!/usr/bin/env python3
"""Cover bank helper (content/cover-bank.json).
  python3 scripts/cover_bank.py status            # unused count per game (+ LOW warning when < 2)
  python3 scripts/cover_bank.py next <mw4|gta6>   # print an UNUSED image + side (does not mark it)
  python3 scripts/cover_bank.py use <file> <slug> # mark used (refuses if already used)
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'content/cover-bank.json')
def load(): return json.load(open(P))
def save(d): json.dump(d, open(P, 'w'), indent=2); open(P, 'a').write('\n')
def status(d):
    games = sorted({i['game'] for i in d['images']})
    for g in games:
        free = [i['file'] for i in d['images'] if i['game'] == g and not i['used_by']]
        print(f"{g}: {len(free)} unused" + ("  <-- LOW: ask the parent to generate more" if len(free) < 2 else ''))
        for f in free: print('   ', f)
if __name__ == '__main__':
    a = sys.argv[1:]; d = load()
    if not a or a[0] == 'status': status(d)
    elif a[0] == 'next':
        g = {'gta': 'gta6', 'warzone': 'mw4'}.get(a[1], a[1])
        free = [i for i in d['images'] if i['game'] == g and not i['used_by'] and os.path.exists(os.path.join(ROOT, i['file']))]
        if not free: sys.exit(f'NO unused bank image for {g}')
        print(f"{free[0]['file']} side={free[0]['side']}")
    elif a[0] == 'use':
        f = a[1].replace(ROOT + '/', '')
        for i in d['images']:
            if i['file'] == f:
                if i['used_by'] and i['used_by'] != a[2]: sys.exit(f"ALREADY USED by {i['used_by']}")
                i['used_by'] = a[2]; save(d); print('marked', f, '->', a[2]); status(d); break
        else: sys.exit('not in bank: ' + f)
    else: print(__doc__)

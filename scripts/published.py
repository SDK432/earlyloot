#!/usr/bin/env python3
"""Published-log helper (content/published-log.csv) for duplicate avoidance.
  python3 scripts/published.py check radio stations      # show past posts matching ALL keywords (title/slug/url)
  python3 scripts/published.py add content/articles/<slug>.md   # append an article to the log
  python3 scripts/published.py today                     # posts already logged for today (box date)"""
import sys, os, csv, datetime, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, 'content/published-log.csv')
HDR = ['date', 'slug', 'game', 'category', 'title', 'primary_source_url']

def rows():
    with open(LOG, newline='') as f: return list(csv.DictReader(f))

cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
if cmd == 'check':
    kw = [k.lower() for k in sys.argv[2:]]
    hits = [r for r in rows() if all(k in ' '.join(r.values()).lower() for k in kw)]
    for r in hits: print(r['date'], r['slug'], '|', r['title'], '|', r['primary_source_url'])
    print(f'{len(hits)} match(es)'); sys.exit(1 if hits else 0)
elif cmd == 'add':
    fm = yaml.safe_load(open(sys.argv[2]).read().split('---')[1])
    if any(r['slug'] == fm['slug'] for r in rows()): sys.exit('already logged: ' + fm['slug'])
    with open(LOG, 'a', newline='') as f:
        csv.writer(f).writerow([str(fm['date']), fm['slug'], fm['game'], fm['category'], fm['title'], fm['sources'][0]['url']])
    print('logged', fm['slug'])
elif cmd == 'today':
    t = str(datetime.date.today()); r = [x for x in rows() if x['date'] == t]
    for x in r: print(x['slug'])
    print(f'{len(r)} post(s) logged for {t}')
else: print(__doc__)

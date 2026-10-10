#!/usr/bin/env python3
"""EarlyLoot static site builder.
content/articles/*.md + content/pages/*.md + site.yml  ->  dist/
Also renders thumbnails (scripts/thumbs.py), sitemap.xml, robots.txt, favicons.
Usage: python3 scripts/build.py [--no-thumbs] [--drafts]"""
import os, re, sys, json, shutil, datetime, html, glob
import yaml, markdown
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thumbs
import thumbs_v2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.environ.get('DIST_DIR') or os.path.join(ROOT, 'dist')
CFG = yaml.safe_load(open(os.path.join(ROOT, 'site.yml')))
URL = CFG['url'].rstrip('/')
NAME = CFG['name']
GAMES = CFG['games']
TODAY = datetime.date.today()
ARGS = sys.argv[1:]
e = html.escape
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()

def fmt(d, long=False):
    return d.strftime('%B %-d, %Y') if long else f"{MONTHS[d.month-1]} {d.day}"

def as_date(v):
    return v if isinstance(v, datetime.date) else datetime.date.fromisoformat(str(v))

def read_md(path):
    raw = open(path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
    if not m: raise SystemExit(f'Missing front matter: {path}')
    meta = yaml.safe_load(m.group(1)) or {}
    md = markdown.Markdown(extensions=['toc', 'tables', 'attr_list', 'sane_lists'],
                           extension_configs={'toc': {'toc_depth': '2'}})
    body = md.convert(m.group(2))
    body = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', body)
    meta['html'] = body
    meta['toc'] = [(t['id'], t['name']) for t in md.toc_tokens]
    meta['words'] = len(re.sub('<[^>]+>', ' ', body).split())
    return meta

# ---------- load content ----------
articles = []
for f in sorted(glob.glob(os.path.join(ROOT, 'content/articles/*.md'))):
    a = read_md(f)
    for k in ('title', 'slug', 'game', 'category', 'date', 'description'):
        if k not in a: raise SystemExit(f'{f}: missing "{k}" in front matter')
    if a['game'] not in GAMES: raise SystemExit(f'{f}: unknown game {a["game"]}')
    a['date'] = as_date(a['date'])
    if a.get('draft') and '--drafts' not in ARGS: continue
    if a['date'] > TODAY and '--drafts' not in ARGS: continue  # scheduled for the future
    a['url'] = f"/articles/{a['slug']}/"
    a['img'] = f"/media/thumbs/{a['slug']}.jpg"
    a['mins'] = max(1, round(a['words'] / 220))
    articles.append(a)
articles.sort(key=lambda a: (a['date'], a.get('featured', False), a['title']), reverse=True)
pages = [read_md(f) for f in sorted(glob.glob(os.path.join(ROOT, 'content/pages/*.md')))]
events = sorted([dict(ev, date=as_date(ev['date'])) for ev in CFG['events']], key=lambda x: x['date'])

# ---------- output dir ----------
if os.path.exists(DIST): shutil.rmtree(DIST)
shutil.copytree(os.path.join(ROOT, 'static'), os.path.join(DIST, 'static'))
os.makedirs(os.path.join(DIST, 'media/thumbs'))

# ---------- thumbnails ----------
cache = os.path.join(ROOT, 'media/thumbs')
os.makedirs(cache, exist_ok=True)
for a in articles:
    t = a.get('thumb') or {}
    out = os.path.join(cache, a['slug'] + '.jpg')
    if '--no-thumbs' not in ARGS or not os.path.exists(out):
        words = a['title'].split()
        if t.get('style') == 'v2':
            thumbs_v2.render(out, t.get('lines') or [t.get('line1', ''), t.get('line2', '')], int(t.get('key', 0)),
                             t.get('label', GAMES.get(a['game'], {}).get('short', '')), t.get('theme', 'fire'),
                             t.get('character'), t.get('side', 'right'), t.get('badge'), t.get('bg'), t.get('bg_mode', 'faint'))
        else:
            thumbs.render(out, a['game'], a['slug'], t.get('line1', ' '.join(words[:2])),
                        t.get('line2', ' '.join(words[2:4])), t.get('accent', 'yellow'),
                        t.get('badge'), a.get('image'))
    shutil.copy(out, os.path.join(DIST, 'media/thumbs'))

# ---------- favicon ----------
def favicons():
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGBA', (512, 512), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 511, 511), 96, fill=(11, 13, 18))
    d.rounded_rectangle((28, 28, 483, 483), 76, fill=(124, 255, 58))
    f = ImageFont.truetype(thumbs.FONT, 380); b = d.textbbox((0, 0), 'E', font=f)
    d.text(((512 - (b[2] - b[0])) / 2 - b[0], (512 - (b[3] - b[1])) / 2 - b[1]), 'E', font=f, fill=(11, 13, 18))
    im.save(os.path.join(DIST, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    im.resize((180, 180), Image.LANCZOS).save(os.path.join(DIST, 'apple-touch-icon.png'))
    im.resize((192, 192), Image.LANCZOS).save(os.path.join(DIST, 'icon-192.png'))
    im.save(os.path.join(DIST, 'icon-512.png'))
favicons()

# ---------- templates ----------
NAV = [('MW4', '/mw4/'), ('ARC Raiders', '/arc-raiders/'), ('GTA VI', '/gta6/'), ('Guides', '/guides/'), ('News', '/news/')]
EV_JSON = json.dumps([{'date': str(x['date']), 'label': x['label'], 'game': x['game']} for x in events])

def logo(): return 'Early<b>Loot</b>'

def layout(path, title, desc, body, og_img=None, og_type='website', extra_head=''):
    canon = URL + path
    img = URL + (og_img or '/media/og-default.jpg')
    navh = ''.join(f'<a href="{u}"{" class=on" if path.startswith(u) else ""}>{n}</a>' for n, u in NAV)
    full_title = title if title.startswith(NAME) else f'{title} | {NAME}'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}"><meta name="theme-color" content="#0b0d12">
<meta property="og:site_name" content="{NAME}"><meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{img}">
<meta property="og:image:width" content="1280"><meta property="og:image:height" content="720">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{img}">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/static/fonts/Anton-Regular.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="/static/style.css">{extra_head}
</head><body>
<header><div class="wrap"><a class="logo d" href="/">{logo()}</a><nav id="nav">{navh}</nav>
<a class="sub" href="/news/">Latest news</a><button class="menu" aria-label="Menu" onclick="document.body.classList.toggle('open')">☰</button></div></header>
{body}
<footer><div class="wrap fgrid"><div><a class="logo d" href="/">{logo()}</a><p>{e(CFG["tagline"])}.</p></div>
<div><h5>Games</h5><a href="/mw4/">Modern Warfare 4</a><a href="/arc-raiders/">ARC Raiders</a><a href="/gta6/">GTA VI</a></div>
<div><h5>Site</h5><a href="/guides/">Guides</a><a href="/news/">News</a><a href="/about/">About</a><a href="/privacy/">Privacy &amp; Disclaimer</a></div></div>
<div class="wrap legal">{NAME} is an independent, fan-made site. Not affiliated with, endorsed or sponsored by Activision, Embark Studios or Rockstar Games. All game names and trademarks belong to their respective owners. Images are our own screenshots or original artwork. © {TODAY.year} {NAME}.</div></footer>
<script>window.DM_EVENTS={EV_JSON};</script><script src="/static/app.js" defer></script>
</body></html>'''

def card(a, big=False):
    g = GAMES[a['game']]
    tagc = 'y' if a['category'] == 'guide' else ''
    return f'''<a class="card" href="{a["url"]}"><img src="{a["img"]}" alt="{e(a["title"])}" loading="lazy" width="1280" height="720">
<div><span class="tag {tagc}">{e(g["short"])} · {a["category"].title()}</span><h3>{e(a["title"])}</h3><p>{e(a["description"])}</p></div></a>'''

def countdown(d, cls=''):
    return f'<span class="cd {cls}" data-countdown="{d}">{fmt(d)}</span>'

def game_box(gk):
    g = GAMES[gk]; evs = [x for x in events if x['game'] == gk]
    rows = ''.join(f'<li><b>{fmt(x["date"])}</b><span>{e(x["label"].split("·")[-1].strip())}</span>{countdown(x["date"])}</li>' for x in evs)
    return f'<a class="card gbox" href="/{gk}/"><div><span class="tag">Key dates</span><h3 class="d">{e(g["name"])}</h3><ul>{rows}</ul><span class="more">All {e(g["short"])} coverage →</span></div></a>'

def calendar():
    li = ''.join(f'<li data-date="{x["date"]}"><b>{fmt(x["date"])}</b><span>{e(x["label"])}</span>{countdown(x["date"])}</li>' for x in events)
    return f'<div class="cal"><h2 class="d">Release Calendar {TODAY.year}</h2><ol>{li}</ol><p class="tz">Countdowns run to midnight in your local time zone. Exact unlock times vary by platform and region.</p></div>'

def write(path, content):
    p = os.path.join(DIST, path.strip('/'), 'index.html') if not path.endswith('.html') else os.path.join(DIST, path.strip('/'))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(content)

# ---------- home ----------
nxt = next((x for x in events if x['major'] and x['date'] >= TODAY), events[-1])
ga = [a for a in articles if a['game'] == nxt['game']]
hero_a = next((a for a in ga if a.get('featured')), ga[0] if ga else articles[0])
g = GAMES[nxt['game']]
hero = f'''<div class="hero"><a href="{hero_a["url"]}"><img src="{hero_a["img"]}" alt="{e(hero_a["title"])}" width="1280" height="720"></a><div>
<span class="tag">Next big launch · {fmt(nxt["date"], True)}</span><h1 class="d">{e(nxt["label"].split("·")[0].strip())}: <span>{e(nxt["label"].split("·")[-1].strip())}</span></h1>
<p>{e(hero_a["description"])}</p>
<div class="clock" data-countdown="{nxt["date"]}" data-clock="1"><div><b>--</b><small>days</small></div><div><b>--</b><small>hours</small></div><div><b>--</b><small>min</small></div><div><b>--</b><small>sec</small></div></div>
<a class="btn" href="{hero_a["url"]}">Read the guide →</a></div></div>'''
latest = ''.join(card(a) for a in articles[:6])
sections = ''
for gk, gv in GAMES.items():
    items = [a for a in articles if a['game'] == gk][:2]
    sections += f'<section><h2 class="st d"><a href="/{gk}/">{e(gv["name"])}</a></h2><div class="grid">{"".join(card(a) for a in items)}{game_box(gk)}</div></section>'
write('/', layout('/', f'{NAME}: Guides & News for MW4, ARC Raiders and GTA VI', CFG['description'],
      f'<main class="wrap">{hero}{calendar()}<section><h2 class="st d">Latest</h2><div class="grid">{latest}</div></section>{sections}</main>',
      og_img=hero_a['img']))

# ---------- game hubs ----------
for gk, gv in GAMES.items():
    items = [a for a in articles if a['game'] == gk]
    evs = [x for x in events if x['game'] == gk]
    dates = ''.join(f'<div class="date"><small>{e(x["label"].split("·")[-1].strip())}</small><span class="d">{fmt(x["date"])}</span>{countdown(x["date"])}</div>' for x in evs)
    body = f'''<main class="wrap"><div class="hub"><span class="tag">Game hub</span><h1 class="d">{e(gv["name"])}</h1><p>{e(gv["blurb"])}</p><div class="dates">{dates}</div></div>
<div class="grid">{"".join(card(a) for a in items) or "<p>Coverage coming soon.</p>"}</div></main>'''
    write(f'/{gk}/', layout(f'/{gk}/', f'{gv["name"]} Guides, News & Release Dates', f'{gv["blurb"]} Guides and news from {NAME}.', body,
          og_img=items[0]['img'] if items else None))

# ---------- category hubs ----------
for cat, title, blurb in [('guide', 'Guides', 'Practical guides and explainers for MW4, ARC Raiders and GTA VI.'),
                          ('news', 'News', 'The latest confirmed news for MW4, ARC Raiders and GTA VI, sourced from official announcements.')]:
    items = [a for a in articles if a['category'] == cat]
    path = f'/{title.lower()}/'
    body = f'<main class="wrap"><div class="hub"><h1 class="d">{title}</h1><p>{blurb}</p></div><div class="grid">{"".join(card(a) for a in items)}</div></main>'
    write(path, layout(path, f'{title}: MW4, ARC Raiders & GTA VI', blurb, body, og_img=items[0]['img'] if items else None))

# ---------- articles ----------
for a in articles:
    g = GAMES[a['game']]
    toc = ''.join(f'<li><a href="#{i}">{e(n)}</a></li>' for i, n in a['toc'])
    src = ''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a></li>' for s in a.get('sources', []))
    related = [x for x in articles if x is not a and x['game'] == a['game']] + [x for x in articles if x['game'] != a['game']]
    upd = f' · Updated {fmt(as_date(a["updated"]), True)}' if a.get('updated') else ''
    ld = json.dumps({'@context': 'https://schema.org', '@type': 'NewsArticle' if a['category'] == 'news' else 'Article',
                     'headline': a['title'], 'description': a['description'], 'image': [URL + a['img']],
                     'datePublished': str(a['date']), 'dateModified': str(a.get('updated', a['date'])),
                     'author': {'@type': 'Organization', 'name': f'{NAME} Staff'},
                     'publisher': {'@type': 'Organization', 'name': NAME, 'logo': {'@type': 'ImageObject', 'url': URL + '/icon-512.png'}},
                     'mainEntityOfPage': URL + a['url']})
    body = f'''<main class="wrap art"><article><div class="crumbs"><a href="/">Home</a> › <a href="/{a["game"]}/">{e(g["name"])}</a> › <a href="/{"guides" if a["category"]=="guide" else "news"}/">{a["category"].title()}</a></div>
<span class="tag {"y" if a["category"]=="guide" else ""}">{e(g["short"])} · {a["category"].title()}</span><h1 class="d">{e(a["title"])}</h1>
<div class="meta">By {NAME} Staff · <time datetime="{a["date"]}">{fmt(a["date"], True)}</time>{upd} · {a["mins"]} min read</div>
<img class="heroimg" src="{a["img"]}" alt="{e(a["title"])}" width="1280" height="720"><div class="body">{a["html"]}</div>
{f'<div class="sources"><h4>Sources</h4><ol>{src}</ol></div>' if src else ''}</article>
<aside><div class="box"><h4>In this article</h4><ol>{toc}</ol></div></aside></main>
<section class="wrap"><h2 class="st d">Read next</h2><div class="grid">{"".join(card(x) for x in related[:3])}</div></section>'''
    write(a['url'], layout(a['url'], a['title'], a['description'], body, og_img=a['img'], og_type='article',
          extra_head=f'<meta property="article:published_time" content="{a["date"]}"><script type="application/ld+json">{ld}</script>'))

# ---------- static pages ----------
for p in pages:
    path = f'/{p["slug"]}/'
    write(path, layout(path, p['title'], p['description'], f'<main class="wrap page"><h1 class="d">{e(p["title"])}</h1><div class="body">{p["html"]}</div></main>'))

write('404.html', layout('/404', 'Page not found', 'This page does not exist.', '<main class="wrap page"><h1 class="d">404: Wrong drop zone</h1><p>This page doesn\'t exist. <a class="btn" href="/">Back to home</a></p></main>'))

# default OG image = hero thumb
shutil.copy(os.path.join(DIST, hero_a['img'].lstrip('/')), os.path.join(DIST, 'media/og-default.jpg'))

# ---------- sitemap / robots ----------
urls = [('/', TODAY)] + [(f'/{k}/', TODAY) for k in GAMES] + [('/guides/', TODAY), ('/news/', TODAY)] \
     + [(a['url'], as_date(a.get('updated', a['date']))) for a in articles] + [(f'/{p["slug"]}/', TODAY) for p in pages]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
     ''.join(f'  <url><loc>{URL}{u}</loc><lastmod>{d}</lastmod></url>\n' for u, d in urls) + '</urlset>\n'
open(os.path.join(DIST, 'sitemap.xml'), 'w').write(sm)
open(os.path.join(DIST, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n')
print(f'Built {len(articles)} articles, {len(pages)} pages, {len(urls)} sitemap URLs -> {DIST}')

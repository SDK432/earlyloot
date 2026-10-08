# EarlyLoot

Fan-made English guides & news site for **Call of Duty: Modern Warfare 4**, **ARC Raiders** and **GTA VI**.
Target domain: **earlyloot.com** (not registered yet). Static HTML, built by a small Python script, so it can be hosted anywhere (Vercel, Railway, Netlify, Cloudflare Pages).

## Quick start

```bash
pip install -r requirements.txt        # markdown, PyYAML, Pillow
python3 scripts/build.py               # -> dist/
python3 -m http.server -d dist 8000    # preview at http://localhost:8000
python3 scripts/shoot.py               # optional: screenshots into preview/ (needs playwright + Chrome)
```

Build flags: `--no-thumbs` reuses existing thumbnails and only renders missing ones. `--drafts` also builds drafts and future-dated articles.

## Folder layout

| Path | What it is |
|---|---|
| `site.yml` | Site name, URL, game hubs and the **release calendar** (it drives the countdowns and the homepage hero) |
| `content/articles/*.md` | Articles (Markdown + YAML front matter) |
| `content/pages/*.md` | Static pages (About, Privacy & Disclaimer) |
| `media/screenshots/<game>/` | Background images for thumbnails: `mw4/`, `arc-raiders/`, `gta6/` |
| `media/thumbs/` | Generated thumbnails (cache, also used as Open Graph images) |
| `static/` | CSS, JS (live countdown), fonts |
| `scripts/build.py` | Builder: pages, thumbnails, sitemap.xml, robots.txt, favicons, 404 |
| `scripts/thumbs.py` | YouTube-style thumbnail renderer (Pillow) |
| `scripts/new_article.py` | Creates a new article skeleton |
| `dist/` | Build output. This is what you deploy. Don't edit by hand. |

## Adding an article (manually or from an automation)

1. Create the file:
   ```bash
   python3 scripts/new_article.py arc-raiders guide "Pendola Pass Shelter Locations" "SHELTER" "MAP" "Guide" green
   ```
   or just drop a `.md` file into `content/articles/` with this front matter:
   ```yaml
   ---
   title: "Pendola Pass Shelter Locations"
   slug: pendola-pass-shelter-locations      # URL: /articles/<slug>/
   game: arc-raiders                         # mw4 | arc-raiders | gta6
   category: guide                           # guide | news
   date: 2026-10-09                          # future date = scheduled (not built until that day)
   updated: 2026-10-10                       # optional
   description: "140-160 chars for Google + social cards"
   thumb: {line1: "SHELTER", line2: "MAP", accent: green, badge: "Guide"}   # accent: yellow | green
   image: my-shot.jpg                        # optional: force a background from media/screenshots/<game>/
   featured: true                            # optional: prefer this article in the homepage hero
   draft: true                               # optional: skip until removed
   sources:
     - {name: "Official source title", url: "https://..."}
   ---
   Body in Markdown. Every `## Heading` becomes a table-of-contents entry. Link official sources inline.
   ```
2. Run `python3 scripts/build.py`. It renders the article page, the thumbnail, the hub/category/home listings, the sitemap and the OG tags.
3. Deploy `dist/` (or push to git if the host builds automatically, see below).

**Editorial rules:** use only facts from official sources (publisher blogs, support pages, press releases), link them inline and in `sources`, publish no leaks as fact, and use no official logos, cover art or wallpapers.

**Automation:** a scheduled job (cron, GitHub Action or agent) only has to write a `.md` file into `content/articles/`, run `build.py` and deploy. Future-dated articles publish themselves on the first build on or after their date, so a daily rebuild also keeps the homepage hero pointed at the next launch.

## Images / screenshots

- Drop your own gameplay screenshots (JPG/PNG/WebP, ideally 1920×1080) into `media/screenshots/<game>/`.
- Real screenshots automatically replace `placeholder-*.jpg`. With several screenshots, each article gets one picked from its slug, so cards vary. Use `image:` to choose a specific one.
- Thumbnails are 1280×720 with big uppercase text (white + yellow/green, black outline, slight tilt) and an optional badge.
- The current `placeholder-ai.jpg` files are AI-generated stand-ins. The ARC Raiders one in particular doesn't look like the game and should be replaced.

## Release calendar & countdowns

Edit `events` in `site.yml`. `static/app.js` counts down live to **local midnight** of each date in the visitor's time zone and switches to "Out today"/"Out now" automatically. The homepage hero shows the next `major` event (chosen at build time), so rebuild at least daily.

## SEO

Every page gets a `<title>`, meta description, canonical URL, Open Graph + Twitter card (the article thumbnail is the OG image) and JSON-LD `Article`/`NewsArticle` on articles. The build also writes `sitemap.xml`, `robots.txt`, favicons (`favicon.ico`, `apple-touch-icon.png`, 192/512 icons) and `404.html`. If the domain changes, update `url:` in `site.yml`.

## Deploying (Railway, same pattern as Boost F1)

- Source: GitHub repo `SDK432/earlyloot` (branch `main`) connected to the Railway service. Every push to `main` builds and deploys automatically.
- `railway.toml`: Railpack (Python, from `requirements.txt` + `.python-version`), build `python scripts/build.py`, start `python scripts/serve.py`, healthcheck `/`.
- `scripts/serve.py` serves `dist/` on `$PORT`, **rebuilds the site every hour in-process** (`REBUILD_HOURS`), so the countdown hero and future-dated articles go live without a redeploy. It also redirects `www.earlyloot.com` to `earlyloot.com` (`CANONICAL_HOST`), serves `404.html`, gzips text and sets cache headers.
- Publishing a new article = commit the `.md` (and optional screenshots) to `main`. Railway rebuilds within a few minutes.
- `vercel.json` is kept only as an alternative and isn't used.

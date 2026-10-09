# EarlyLoot news runbook (3 posts/day, auto-publish)

Repo: `/workspace/gaming-site` → GitHub `SDK432/earlyloot` (branch `main`) → Railway project **EarlyLoot**
(service `earlyloot` 713ad248-305c-47c4-92ef-69e96a9e8451, env production ee503faa-8f61-4eeb-bc68-ad1ae613884d).
Every push to `main` auto-deploys. Live: https://earlyloot.com. **Never touch the Boost F1 project.**
Times: America/Guayaquil (UTC-5).

## 0. Before you start
```bash
cd /workspace/gaming-site && git pull --ff-only   # (pull is public, no token needed)
python3 scripts/published.py today                # how many already went out today (target: 3)
```
Rotate games across the day (e.g. one each of GTA VI, MW4/Warzone and ARC Raiders) when the news allows. Freshness beats rotation.

## 1. Find news (last 24–48 h)
- Official sources first:
  - Rockstar Newswire (rockstargames.com/newswire) and rockstargames.com/VI
  - callofduty.com/blog
  - PlayStation Blog and Xbox Wire
  - arcraiders.com/news (including patch notes)
  - Official X accounts, as quoted by outlets
- Then reputable outlets for confirmation and context: IGN, Kotaku, Push Square, Eurogamer, PC Gamer, VGC, NME, Dexerto (only when they cite official sources).
- Example WebSearch queries, always with the current date: "GTA 6 news October 9 2026", "Modern Warfare 4 Warzone update today", "ARC Raiders patch notes October 2026".
- **Duplicate check, which is mandatory:** `python3 scripts/published.py check <2-3 keywords>`. Exit code 1 means it matches an earlier post.
  - Only write about the same topic again if there is a genuinely new development. Then use a new angle and slug, and link to the earlier article.
  - Also run `ls content/articles` and `rg -il "<keyword>" content/articles`.
- Pick the single biggest, verifiable story. Skip leaks, rumours and datamines (or clearly label them as unconfirmed; never present them as fact).

## 2. Write (400–600 words, English, original)
```bash
python3 scripts/new_article.py <mw4|arc-raiders|gta6> news "SEO Title"   # creates a draft skeleton
```
- Fill in the front matter:
  - `title` is the longer SEO title, punchy and accurate. Example: "GTA 6 Radio Stations Revealed: Flash FM Returns, …".
  - Also set `slug`, `game`, `category: news`, `date: YYYY-MM-DD` (today; future dates are hidden until that day), `description` (max ~155 characters), `sources` (first source = the primary official URL) and `thumb` (see 3).
  - **Remove `draft: true`** so the post publishes.
- Body:
  - A lead paragraph with the key fact, the date and an inline link to the official source.
  - `##` sections (they become the table of contents).
  - Bullets for lists, and a "What's next" section with dates.
  - Inline links on every fact. Put third-party claims under the outlet's name ("Pitchfork reports…").
  - Link internally to related EarlyLoot articles (`/articles/<slug>/`).
- Don't copy sentences from sources. Quote briefly, with quotation marks and attribution.
- No official logos, cover art, key art or wallpapers anywhere.

## 3. Thumbnail (style v2, 1280x720)
Front matter:
```yaml
thumb: {style: v2, label: "GTA VI", lines: ["RADIO", "REVEALED"], key: 0, theme: neon, character: prop-boombox.png, side: right, badge: "NEW"}
```
- `label`: the game name as **plain bold text** (WARZONE, MW4, ARC RAIDERS, GTA VI). Never use the official logo or its lettering.
- `lines`: 2–4 words in total. `key` is the index of the huge yellow word; the other lines are white.
- `theme`:
  - `fire` (red/orange): good for CoD/Warzone.
  - `volt` (yellow).
  - `neon` (pink/orange): good for GTA/Vice City.
  - `ice` (blue): good for ARC Frozen Trail and winter.
- `character`: a transparent PNG in `media/characters/`. `side` is left or right; the text goes on the opposite side.
  - Available: `mw4-skull-operator.png` (original hooded skull-balaclava operator, best for CoD/Warzone), `mw4-operator.png`, `arc-raider.png`, `gta6-convertible.png` (low resolution, avoid large use), `prop-boombox.png`.
  - New characters must be ORIGINAL look-alikes (e.g. a hooded operator with a generic skull-print balaclava, an extraction raider, a weapon close-up). Never Ghost or any official character, and no logos.
  - Generate on a plain background (GenerateImage, done by the parent agent), then cut out:
    ```bash
    python3 -c "from rembg import remove,new_session;from PIL import Image;s=new_session('isnet-general-use');remove(Image.open('in.png'),session=s).save('media/characters/NAME.png')"
    ```
  - Vector props: `scripts/draw_props.py`.
- Optional `bg: media/screenshots/...jpg` adds a faint, colour-graded scene under the rays.
- Old-style thumbnails (`line1/line2/accent`) still work.
- Preview: `python3 scripts/build.py`, then view `media/thumbs/<slug>.jpg`. Check that the text is readable and nothing is cut off.

## 4. Build and check locally
```bash
python3 scripts/build.py          # must print "Built N articles…" without errors
python3 scripts/shoot.py          # optional screenshots into preview/
python3 scripts/published.py add content/articles/<slug>.md
```

## 5. Publish
```bash
git add -A && git -c user.name="EarlyLoot" -c user.email="y2rick432@gmail.com" commit -m "News: <short title>"
B64=$(printf 'x-access-token:%s' "$GITHUB_TOKEN_EARLYLOOT" | base64 -w0); \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $B64" push origin main 2>&1 | sed -E 's/(basic|token) [A-Za-z0-9+/=_]+/\1 ***/g'; unset B64
```
- **Never** print or echo the token, or write it to files, git config, remotes or logs. The remote must stay `https://github.com/SDK432/earlyloot.git`. Verify with `git remote -v` and `git config --list | rg -i extraheader` (expect no output).

## 6. Verify the deploy
- Railway MCP: `list-deployments` (service above). Wait until the newest deployment is **SUCCESS**, usually 2–4 minutes. If it is FAILED, run `get-logs` (build) and fix.
- **Known issue (Oct 9, 2026): pushes do NOT auto-trigger a deploy yet.** The Railway GitHub app probably doesn't have access to this repo; Rick can fix that in GitHub → Settings → Applications → Railway → Repository access. Until then, after every push call Railway `connect-service-source` with projectId `9da86bbb-e909-41d3-b698-ac30f18c90d2`, serviceId `713ad248-305c-47c4-92ef-69e96a9e8451`, repo `SDK432/earlyloot` and branch `main`. It immediately deploys the latest commit of main.
- `curl -s -o /dev/null -w '%{http_code}\n' https://earlyloot.com/articles/<slug>/` should return 200. Also check that the home page lists it and the thumbnail at `/media/thumbs/<slug>.jpg` returns 200.
- The server also rebuilds hourly, so date-scheduled posts appear automatically on their date.

## 7. Report
Report the title, live URL, sources, thumbnail path, deploy ID and status, and any issues.

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
thumb: {style: v2, label: "GTA VI", lines: ["RADIO", "REVEALED"], key: 0, theme: neon, bg: media/characters/gta6-<scene>.jpg, bg_mode: full, side: left, badge: "NEW"}
```
- `label`: the game name as **plain bold text** (WARZONE, MW4, ARC RAIDERS, GTA VI). Never use the official logo or its lettering.
- `lines`: 2–4 words in total. `key` is the index of the huge yellow word; the other lines are white.
- `theme`:
  - `fire` (red/orange): good for CoD/Warzone.
  - `volt` (yellow).
  - `neon` (pink/orange): good for GTA/Vice City.
  - `ice` (blue): good for ARC Frozen Trail and winter.
- `character`: a transparent PNG in `media/characters/`. For ARC Raiders, use Rick's cutouts (see below). `side` is left or right; the text goes on the opposite side.
  - Available: `mw4-rick-01..08.png` (Rick's MW4/Warzone operators, **the only ones allowed for MW4/Warzone**, see below), `arc-raider.png`, `gta6-convertible.png` (low resolution, avoid large use).
  - New characters must be ORIGINAL look-alikes (e.g. a hooded operator with a generic skull-print balaclava, an extraction raider, a weapon close-up). Never Ghost or any official character, and no logos.
  - Generate on a plain background (GenerateImage, done by the parent agent), then cut out:
    ```bash
    python3 -c "from rembg import remove,new_session;from PIL import Image;s=new_session('isnet-general-use');remove(Image.open('in.png'),session=s).save('media/characters/NAME.png')"
    ```
  - **NEVER use drawn/vector props (`scripts/draw_props.py`, `prop-*.png` such as the helicopter or boombox) for ANY game.** Rick rejected them; `thumbs_v2.py` now refuses them.
- **GTA VI thumbnails MUST ALWAYS be a freshly generated, photoreal, cinematic full-bleed scene** (GenerateImage, done by the parent agent), in the style of Rick's GTA references: warm orange/pink sunset or neon city, police helicopters with searchlights over a skyline, muscle cars, highways at golden hour, beaches, Vice City vibe. No logos, no real people, no official characters, never the reference images themselves (they may be official art).
  - Use it as `bg: media/characters/gta6-<scene>.jpg`, `bg_mode: full`, no `character:`, `side: left` (text side). New scene every post; never reuse an earlier GTA image (check `rg -n "^thumb" content/articles/gta-*.md`).
  - GenerateImage returns a path outside the repo: copy it into `media/characters/gta6-<scene>.jpg` IMMEDIATELY after generating (`cp <returned path> media/characters/gta6-<scene>.jpg`), before doing anything else.
  - Before building, confirm the generated file exists on disk (`ls -la media/characters/gta6-<scene>.jpg`) and look at it: it must be photoreal with no drawn/cartoon elements. If the image can't be saved, retry generating; NEVER fall back to props or placeholders.
- Optional `bg: media/screenshots/...jpg` adds a faint, colour-graded scene under the rays (default `bg_mode: faint`); `bg_mode: full` uses the real scene, colour-graded, as the background.
- **ARC Raiders thumbnails MUST use Rick's own gameplay images** (never the AI placeholder):
  - Clean HUD-free scenes (1600x900): `media/screenshots/arc-raiders/clean/arc-01.jpg` … `arc-06.jpg`. Use them as `bg:` with `bg_mode: full`.
    - 01: forest/rocks; 02: misty path with a downed ARC; 03: swamp boardwalk/tunnel; 04: industrial dome interior; 05: top-down metal floor; 06: rainy open field.
  - Raider cutouts: `media/characters/arc-raider-rick-01.png`, `-02.png`, `-06.png`. Use them as `character:` (they're cut at the waist and sit on the bottom edge automatically).
  - **Rotate:** don't reuse the previous ARC post's character or background. Check what's been used with `rg -n "^thumb" content/articles/arc-*.md`, pick a different character/bg pair, and don't put a cutout on its own source screenshot (e.g. avoid rick-02 on arc-02).
  - Example: `thumb: {style: v2, label: "ARC RAIDERS", lines: ["HOTFIX", "IS LIVE"], key: 0, theme: ice, character: arc-raider-rick-02.png, side: right, bg: media/screenshots/arc-raiders/clean/arc-05.jpg, bg_mode: full, badge: "NEW"}`
  - New screenshots from Rick: put the raw PNGs at `media/screenshots/arc-raiders/rick-arc-NN.png` (they're gitignored). Add their crop and inpaint rectangles to `scripts/clean_shots.py` and run it. Visually confirm that no HUD remains, especially the player name, the ID string bottom-right, the compass and the prompts. Cut out with rembg (see 3), keeping only the largest component and filling holes.
- **MW4/Warzone thumbnails (DEFAULT, Rick's rule since Oct 15 2026): a freshly generated, photoreal, cinematic full-bleed scene of ORIGINAL tactical operators** (helmets, goggles, balaclavas, NO visible faces, no Ghost/official characters, no logos) in action: squads in smoky streets, fire and debris, rooftops, jungles, etc. Different scene every post (check `rg -n "^thumb" content/articles/mw4-*.md content/articles/warzone-*.md`).
  - Generate with GenerateImage, then copy the returned path into `media/characters/wz-<scene>.jpg` IMMEDIATELY and confirm with `ls -la` before building. Look at it: photoreal, no drawn props. If saving fails, retry generating.
  - Thumb: `bg: media/characters/wz-<scene>.jpg, bg_mode: full`, no `character:`, `side` chosen so the text sits over the emptier half. Same yellow/white outlined text; `label` is plain text WARZONE or MW4.
  - Example: `thumb: {style: v2, label: "WARZONE", lines: ["SEASON 1", "IS COMING"], key: 0, theme: fire, bg: media/characters/wz-squad-street.jpg, bg_mode: full, side: right, badge: "NEW"}`
- **Fallback only** (when a generated image is impossible): Rick's own screenshots/cut-outs, rules below.
- **MW4/Warzone thumbnails fallback: Rick's own screenshots/cut-outs.** Never the old AI operators (`mw4-skull-operator.png`, `mw4-operator.png`) or `media/screenshots/mw4/placeholder-ai.jpg`, and never old-style thumbs for MW4.
  - Operator cut-outs (`character:`): `media/characters/mw4-rick-01.png` … `-08.png`. 01–03: purple-haired operator (01 full body, 02 aiming, 03 upper body with rifle); 04–08: red-masked hooded ninja operator (04 aiming, 05 rifle across chest, 06 full body aiming, 07 side view, 08 close-up).
  - Clean HUD-free scenes (`bg:` with `bg_mode: full`), 1600x900, in `media/screenshots/mw4-warzone/clean/`: 11 shooting range, 12 parachute over the island, 13 rooftop pre-deploy, 14 rooftop with red smoke, 15 interior corridor, 16 helicopter over the island. 01–10 are lobby close-ups of the operators (good as a solo full background with no cut-out; don't put a cut-out on top of its own source shot).
  - **Rotate, and consecutive posts must never repeat an image.** Run `python3 scripts/mw4_images.py next`: it suggests the least-recently-used character + scene, never the previous post's, never a cut-out on its own source shot. After writing the post, record it with `python3 scripts/mw4_images.py use <slug> <character.png> <bg path>`. The log is `content/mw4-image-usage.json` (committed).
  - Example: `thumb: {style: v2, label: "WARZONE", lines: ["NEW", "MAP"], key: 1, theme: fire, character: mw4-rick-03.png, side: right, bg: media/screenshots/mw4-warzone/clean/mw4-14.jpg, bg_mode: full, badge: "NEW"}`
  - `label` is plain text only (WARZONE, MW4, MW4 DMZ). Never the official logo, lettering or the in-game MW4 banner.
  - New screenshots from Rick: put raw PNGs at `media/screenshots/mw4-warzone/rick-mw4-NN.png` (gitignored). Add a crop box and inpaint rects to `scripts/clean_mw4.py` and run it; for cut-outs add the shot to `CUTS` in `scripts/cutout_mw4.py`, then add the new files to `SOURCE` in `scripts/mw4_images.py`. Visually confirm that no UI remains: WARZONE logo, nav bar, MW4 "RESERVAR" banner, left panels, party list/speaker icon, minimap, compass, countdown, prompts, ammo widget, and **every gamertag**.
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

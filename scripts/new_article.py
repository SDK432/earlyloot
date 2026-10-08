#!/usr/bin/env python3
"""Create a new article skeleton.
Usage: python3 scripts/new_article.py <game: mw4|arc-raiders|gta6> <guide|news> "Title" ["LINE1" "LINE2" badge accent]"""
import sys, re, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
game, cat, title = sys.argv[1:4]
extra = sys.argv[4:8]; defaults = ['', '', 'Guide' if cat == 'guide' else 'News', 'yellow']
l1, l2, badge, accent = (extra + defaults[len(extra):])[:4]
slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:70]
path = os.path.join(ROOT, 'content/articles', slug + '.md')
if os.path.exists(path): sys.exit(f'exists: {path}')
words = title.split()
open(path, 'w').write(f'''---
title: "{title}"
slug: {slug}
game: {game}
category: {cat}
date: {datetime.date.today()}
description: "TODO: 140-160 character summary for Google and social cards."
thumb: {{line1: "{l1 or ' '.join(words[:2])}", line2: "{l2 or ' '.join(words[2:4])}", accent: {accent}, badge: "{badge}"}}
draft: true
sources:
  - {{name: "TODO official source", url: "https://"}}
---
Intro paragraph with an [inline link to the official source](https://).

## First section
''')
print(path)

"""Render preview screenshots of dist/ (serves it locally on :8765). Usage: python3 scripts/shoot.py"""
import os, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST=os.path.join(ROOT,'dist'); OUT=os.path.join(ROOT,'preview'); PORT=8765
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
H=functools.partial(Q,directory=DIST)
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(('127.0.0.1',PORT),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
SHOTS=[('home-desktop','/',1440,False),('home-mobile','/',390,True),
       ('article-desktop','/articles/arc-raiders-frozen-trail-pendola-pass/',1440,False),
       ('hub-gta6-desktop','/gta6/',1440,False),('article-mobile','/articles/gta-6-preload-date/',390,True)]
errors=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    for n,path,w,m in SHOTS:
        pg=b.new_page(viewport={'width':w,'height':900},device_scale_factor=2 if m else 1,is_mobile=m)
        pg.on('console',lambda msg: msg.type=='error' and errors.append(msg.text))
        pg.on('response',lambda r: r.status>=400 and errors.append(f'{r.status} {r.url}'))
        pg.goto(f'http://127.0.0.1:{PORT}{path}',wait_until='networkidle'); pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')"); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(1200)
        pg.screenshot(path=f'{OUT}/{n}.png',full_page=True); print('saved',f'{OUT}/{n}.png')
srv.shutdown(); print('errors:',errors or 'none')

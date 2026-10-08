#!/usr/bin/env python3
"""Production static server for EarlyLoot (Railway).
- Serves the built site from dist/ on $PORT (default 8080).
- Rebuilds the site in-process every REBUILD_HOURS (default 1) so the countdown hero
  and future-dated (scheduled) articles update without a redeploy. Builds go to a fresh
  directory and are swapped in atomically; a failed rebuild keeps the old site.
- Redirects www.<domain> -> apex (CANONICAL_HOST, default earlyloot.com), serves 404.html,
  sets cache headers and gzip for text assets."""
import os, sys, time, gzip, shutil, threading, subprocess, http.server, socketserver
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('PORT', '8080'))
CANON = os.environ.get('CANONICAL_HOST', 'earlyloot.com')
HOURS = float(os.environ.get('REBUILD_HOURS', '1'))
STATE = {'dir': os.path.join(ROOT, 'dist')}
TEXT = ('.html', '.css', '.js', '.xml', '.txt', '.svg', '.json')

def build():
    out = os.path.join(ROOT, f'dist-{int(time.time())}')
    env = dict(os.environ, DIST_DIR=out)
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts/build.py'), '--no-thumbs'], env=env, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(os.path.join(out, 'index.html')):
        print('rebuild FAILED, keeping current site\n', r.stdout, r.stderr, flush=True); shutil.rmtree(out, ignore_errors=True); return
    old = STATE['dir']; STATE['dir'] = out
    print('rebuilt:', r.stdout.strip(), flush=True)
    if os.path.basename(old).startswith('dist-'):
        threading.Timer(120, shutil.rmtree, args=(old,), kwargs={'ignore_errors': True}).start()

def loop():
    while True:
        time.sleep(HOURS * 3600)
        try: build()
        except Exception as e: print('rebuild error', e, flush=True)

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=STATE['dir'], **k)
    def log_message(self, fmt, *a): pass
    def _redirect(self):
        host = (self.headers.get('Host') or '').split(':')[0].lower()
        if host == 'www.' + CANON:
            self.send_response(301); self.send_header('Location', f'https://{CANON}{self.path}'); self.end_headers(); return True
        return False
    def end_headers(self):
        p = self.path.split('?')[0]
        if p.startswith(('/static/', '/media/')) or p.endswith(('.ico', '.png')):
            self.send_header('Cache-Control', 'public, max-age=604800')
        else:
            self.send_header('Cache-Control', 'public, max-age=300')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path) and not self.path.split('?')[0].endswith('/'):
            return super().send_head()  # 301 to trailing slash
        if os.path.isdir(path): path = os.path.join(path, 'index.html')
        if not os.path.isfile(path):
            body = open(os.path.join(STATE['dir'], '404.html'), 'rb').read()
            self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body))); self.end_headers()
            return __import__('io').BytesIO(body)
        if path.endswith(TEXT) and 'gzip' in (self.headers.get('Accept-Encoding') or ''):
            data = gzip.compress(open(path, 'rb').read(), 6)
            self.send_response(200); self.send_header('Content-Type', self.guess_type(path))
            self.send_header('Content-Encoding', 'gzip'); self.send_header('Vary', 'Accept-Encoding')
            self.send_header('Content-Length', str(len(data))); self.end_headers()
            return __import__('io').BytesIO(data)
        return super().send_head()
    def do_GET(self):
        if not self._redirect(): super().do_GET()
    def do_HEAD(self):
        if not self._redirect(): super().do_HEAD()

if __name__ == '__main__':
    build()  # fresh build at boot so dates are current even if the image is old
    threading.Thread(target=loop, daemon=True).start()
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    with socketserver.ThreadingTCPServer(('0.0.0.0', PORT), H) as s:
        print(f'EarlyLoot serving {STATE["dir"]} on :{PORT}', flush=True); s.serve_forever()

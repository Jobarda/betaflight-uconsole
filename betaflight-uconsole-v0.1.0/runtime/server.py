#!/usr/bin/env python3
import http.server, os, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT/'current/web'),**kwargs)
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
if __name__ == '__main__':
    port = int(os.environ.get('BETAFLIGHT_UCONSOLE_PORT','5176'))
    if not 1024 <= port <= 65535: raise SystemExit('Port must be 1024..65535')
    http.server.ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()

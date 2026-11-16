#!/usr/bin/env python3
"""Check built web assets over real loopback HTTP without systemd or hardware."""
import functools, http.server, pathlib, threading, urllib.request
root = pathlib.Path(__file__).resolve().parents[1]/'work/bundle/web'
handler = functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
server = http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
thread = threading.Thread(target=server.serve_forever,daemon=True)
thread.start()
try:
    with urllib.request.urlopen('http://127.0.0.1:'+str(server.server_port)+'/index.html') as r:
        assert r.status == 200 and b'<html' in r.read().lower()
finally:
    server.shutdown()
    server.server_close()

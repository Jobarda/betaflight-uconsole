import http.server, importlib.util, io, os, pathlib, tempfile, threading, unittest, urllib.error, urllib.request
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('server',ROOT/'runtime/server.py')
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)

class ServerTests(unittest.TestCase):
    def test_request_handler_without_network(self):
        class Connection:
            def __init__(self,path):
                self.input = io.BytesIO(('GET '+path+' HTTP/1.0\r\n\r\n').encode())
                self.output = bytearray()
            def makefile(self,*args): return self.input
            def sendall(self,data): self.output.extend(data)
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            (base/'current/web').mkdir(parents=True)
            (base/'current/web/index.html').write_text('<html>fixture</html>')
            (base/'secret.txt').write_text('private fixture')
            with mock.patch.object(server_module,'ROOT',base):
                connection = Connection('/index.html')
                server_module.Handler(connection,('127.0.0.1',1),None)
                self.assertIn(b'200 OK',connection.output)
                self.assertIn(b'<html>fixture</html>',connection.output)
                connection = Connection('/../secret.txt')
                server_module.Handler(connection,('127.0.0.1',1),None)
                self.assertIn(b'404',connection.output)
                self.assertNotIn(b'private fixture',connection.output)
    @unittest.skipIf(os.environ.get('BETAFLIGHT_TEST_NO_NETWORK') == '1','Network unavailable in this validation environment')
    def test_serves_only_current_web(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            web = base/'current/web'
            web.mkdir(parents=True)
            (web/'index.html').write_text('<html>fixture</html>')
            (base/'secret.txt').write_text('not a public asset')
            with mock.patch.object(server_module,'ROOT',base):
                server = http.server.ThreadingHTTPServer(('127.0.0.1',0),server_module.Handler)
                thread = threading.Thread(target=server.serve_forever,daemon=True)
                thread.start()
                url = 'http://127.0.0.1:'+str(server.server_port)
                try:
                    with urllib.request.urlopen(url+'/index.html') as response:
                        self.assertEqual(response.read(),b'<html>fixture</html>')
                        self.assertEqual(response.headers['Cache-Control'],'no-store')
                    with self.assertRaises(urllib.error.HTTPError) as error:
                        urllib.request.urlopen(url+'/../secret.txt')
                    self.assertEqual(error.exception.code,404)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()

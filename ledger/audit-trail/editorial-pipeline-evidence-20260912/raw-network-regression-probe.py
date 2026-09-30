"""Run against an unchanged PR50 checkout or its candidate; HTTP/DNS are mocked."""
import importlib.util
import io
import socket
import sys
from contextlib import ExitStack
from email.message import Message
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('probe_runner', root / '_scripts/auto-capture-runner.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
al = {'allow': {'manufacturer.example': {'level': 2, 'license_status': 'unknown', 'source_type': 'technical_datasheet'}}, 'deny': {}}


class Response:
    status = 200
    def __init__(self, body, robots=False):
        self.headers = Message()
        self.headers['Content-Type'] = 'text/plain' if robots else 'text/html'
        self.stream = io.BytesIO(body)
    def read(self, n=-1):
        return self.stream.read(n)
    read1 = read
    def getheader(self, key, default=None):
        return self.headers.get(key, default)
    def __enter__(self):
        return self
    def __exit__(self, *a):
        pass


cases = [
    ('HTTP scheme', 'http://manufacturer.example/x', '93.184.216.34', b'<html>valid page</html>'),
    ('private DNS', 'https://manufacturer.example/x', '127.0.0.1', b'<html>private service</html>'),
    ('oversized stream', 'https://manufacturer.example/x', '93.184.216.34', b'<html>' + b'x' * (2 * 1024 * 1024)),
    ('PDF as HTML', 'https://manufacturer.example/x', '93.184.216.34', b'%PDF-1.7 disguised binary'),
]
refused = 0
for name, url, ip, body in cases:
    class Connection:
        sock = None
        def __init__(self, *a):
            pass
        def request(self, method, path, headers):
            self.path = path
        def getresponse(self):
            return Response(b'User-agent: *\nAllow: /\n', True) if self.path == '/robots.txt' else Response(body)
        def close(self):
            pass
    with ExitStack() as stack:
        stack.enter_context(patch.object(r, 'load_allowlist', return_value=al))
        if hasattr(r, '_http'):
            stack.enter_context(patch.object(r._http.socket, 'getaddrinfo', return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, 443))]))
            stack.enter_context(patch.object(r._http, '_PinnedHTTPSConnection', Connection))
        else:
            stack.enter_context(patch.object(r.urlrequest, 'urlopen', return_value=Response(body)))
        try:
            r.fetch(url)
        except ValueError as exc:
            print(f'REFUSED {name}: {exc}')
            refused += 1
        else:
            print(f'ACCEPTED_UNSAFE {name}')
print(f'{refused}/{len(cases)} unsafe cases refused')
sys.exit(0 if refused == len(cases) else 1)

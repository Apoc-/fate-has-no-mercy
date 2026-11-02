"""Loopback-only editor: explicit routes, bounded JSON, no filesystem API."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from .core import MAX_BYTES, render, validate


def generation_request(request):
    """HTTP bounds are deliberately stricter than the total JSON byte limit."""
    if not isinstance(request, dict):
        raise ValueError('request must be an object')
    choices = {'kind': ('npc', 'location'), 'ruleset': ('neutral', 'core', 'condensed', 'accelerated'),
               'tier': ('mook', 'supporting', 'main'), 'genre': ('fantasy', 'noir', 'scifi'),
               'mode': ('place', 'scene')}
    if set(request) - (set(choices) | {'seed', 'name', 'location_name', 'context'}):
        raise ValueError('Unsupported generation request parameter')
    for key, options in choices.items():
        if key in request and request[key] not in options:
            raise ValueError(f'{key} must be one of: {", ".join(options)}')
    for key, limit in (('name', 200), ('location_name', 200), ('context', 4000)):
        if key in request and (not isinstance(request[key], str) or len(request[key]) > limit):
            raise ValueError(f'{key} must be a string of at most {limit} characters')
    if 'seed' in request:
        check_seed(request['seed'])
    return request


def check_seed(seed):
    from .generator import _seed
    _seed(seed)


def semantic_response(operation, payload):
    """GM workspace API: draft responses contain secrets even in public preview.

    Only the separately projected `card` is a public-shareable artifact. The
    legacy export routes receive just that card (or explicit authoring edits).
    """
    allowed = {'audience', 'detail'} | ({'request'} if operation == 'generate' else {'draft'})
    if operation == 'reroll':
        allowed |= {'seed', 'group'}
    if set(payload) - allowed:
        raise ValueError('Unsupported API parameter')
    audience, detail = payload.get('audience', 'gm'), payload.get('detail', 'compact')
    if audience not in ('gm', 'public'):
        raise ValueError('audience must be gm or public')
    if detail not in ('compact', 'full'):
        raise ValueError('detail must be compact or full')
    if operation == 'generate':
        generation_request(payload.get('request'))
    elif not isinstance(payload.get('draft'), dict):
        raise ValueError('draft must be an object')
    if operation == 'reroll':
        if payload.get('group', 'presentation') != 'presentation':
            raise ValueError('Only presentation rerolls are supported')
        if payload.get('seed') is not None:
            check_seed(payload['seed'])
    from . import generator
    if operation == 'generate':
        draft = generator.generate(payload['request'])
    else:
        draft = payload['draft']
        generator.validate_draft(draft)
        if operation == 'reroll':
            draft = generator.reroll(draft, group='presentation', seed=payload.get('seed'))
    projected = validate(generator.project(draft, audience=audience, detail=detail))
    # Generated public JSON must never carry hidden extension objects. Generic
    # authored cards retain the existing renderer contract, including extensions.
    card = {key: projected[key] for key in ('version', 'kind', 'title', 'subtitle', 'tags', 'fields') if key in projected}
    card['fields'] = [{'label': field['label'], 'value': field['value']} for field in card['fields']]
    return {'card': card} if operation == 'project' else {'draft': draft, 'card': card}


class Handler(BaseHTTPRequestHandler):
    timeout = 5

    def log_message(self, *args):
        pass

    def reply(self, status, body, mime='text/plain; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self' blob:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def allowed(self):
        hosts = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        host = self.headers.get('Host')
        if host not in hosts or self.headers.get('Origin') not in (None, 'http://' + host):
            self.reply(403, b'Only same-origin loopback requests are allowed')
            return False
        return True

    def do_GET(self):
        if not self.allowed(): return
        routes = {'/': ('ui.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if self.path not in routes:
            self.reply(404, b'Not found')
            return
        file, mime = routes[self.path]
        self.reply(200, Path(__file__).with_name(file).read_bytes(), mime)

    def do_POST(self):
        if not self.allowed(): return
        format = self.path.removeprefix('/api/')
        if self.path not in ('/api/svg', '/api/png', '/api/text', '/api/json', '/api/generate', '/api/project', '/api/reroll'):
            self.reply(404, b'Not found')
            return
        try:
            length = int(self.headers.get('Content-Length', '-1'))
            if length < 0 or length > MAX_BYTES:
                self.reply(413, b'JSON request must be at most 65536 bytes')
                return
            if self.headers.get('Content-Type') != 'application/json':
                raise ValueError('Content-Type must be application/json')
            raw = self.rfile.read(length)
            if len(raw) != length: raise ValueError('Incomplete JSON request')
            try:
                payload = json.loads(raw.decode('utf-8'))
            except RecursionError:
                raise ValueError('JSON nesting exceeds the decoder limit') from None
            if not isinstance(payload, dict): raise ValueError('Request must be an object')
            if format in ('generate', 'project', 'reroll'):
                result = semantic_response(format, payload)
                self.reply(200, json.dumps(result, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
                return
            card = validate(payload.get('card'))
            theme = payload.get('theme', 'dark')
            if theme not in ('dark', 'parchment'): raise ValueError('UI theme must be dark or parchment')
            body = json.dumps(card, ensure_ascii=False, indent=2).encode() if format == 'json' else render(card, format, theme)
            mime = {'json': 'application/json; charset=utf-8', 'svg': 'image/svg+xml', 'png': 'image/png', 'text': 'text/plain; charset=utf-8'}[format]
            self.reply(200, body, mime)
        except (ValueError, UnicodeError, OSError) as exc:
            self.reply(400, str(exc).encode('utf-8'))


def make_server(host='127.0.0.1', port=8765):
    if host not in ('127.0.0.1', 'localhost'):
        raise ValueError('Only loopback hosts are supported')
    return ThreadingHTTPServer((host, port), Handler)

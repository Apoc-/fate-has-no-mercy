import unittest
import importlib

class CardTests(unittest.TestCase):
    def test_contract_validation(self):
        core = importlib.import_module('cardmaker.core')
        card = {'version': 1, 'kind': 'note', 'title': 'Test', 'tags': [], 'fields': []}
        self.assertEqual(core.validate(card), card)
        for patch in ({'version': 2}, {'kind': 'bad'}, {'title': ''}, {'fields': [{'label': 'A', 'value': 4}]}, {'tags': 'bad'}):
            with self.assertRaisesRegex(ValueError, '.+'):
                core.validate(dict(card, **patch))

    def test_invalid_xml_characters_and_oversize_rejected(self):
        from cardmaker.core import validate
        card = {'version':1,'kind':'note','title':'Title','tags':[],'fields':[]}
        for title in ('bad\uffff', 'bad\ud800', 'x' * 65536):
            with self.assertRaises(ValueError):
                validate(dict(card, title=title))

class RenderTests(unittest.TestCase):
    def test_portable_render_wrap_escape_autoheight_and_png(self):
        from cardmaker import core
        import xml.etree.ElementTree as ET
        from PIL import Image
        import io
        card = {'version': 1, 'kind': 'npc', 'title': '<Méra & Co>', 'tags': ['fiction'], 'fields': [{'label': 'Story', 'value': ('Longword' * 30 + '\n') * 30 + 'FINAL Ω'}]}
        svg = core.render(card, 'svg')
        root = ET.fromstring(svg)
        self.assertNotIn('foreignObject', svg.decode())
        self.assertIn('FINAL Ω', ''.join(root.itertext()))
        self.assertGreater(int(root.attrib['height']), 1000)
        image = Image.open(io.BytesIO(core.render(card, 'png')))
        self.assertEqual(image.height, int(root.attrib['height']))
        self.assertIn('FINAL Ω', core.render(card, 'text').decode())
        self.assertNotEqual(core.render(card, 'svg', 'parchment'), svg)

    def test_wide_unicode_lines_fit_and_png_resource_limit(self):
        from cardmaker import core
        import xml.etree.ElementTree as ET
        import unicodedata
        card = {'version':1,'kind':'note','title':'Ｗ' * 90,'tags':[],'fields':[{'label':'Wide','value':'Ｗ' * 100}]}
        root = ET.fromstring(core.render(card, 'svg'))
        for node in root.findall('{http://www.w3.org/2000/svg}text'):
            units = sum(2 if unicodedata.east_asian_width(c) in ('F','W') else 1 for c in node.text or '')
            self.assertLessEqual(units, 32 if node.attrib['font-size'] == '24' else 48)
        card['fields'][0]['value'] = '\n' * 20000
        with self.assertRaisesRegex(ValueError, 'PNG.*limit'):
            core.render(card, 'png')

class CLITests(unittest.TestCase):
    def test_cli_text_and_invalid_input(self):
        import subprocess, json, tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'card.json'
            source.write_text(json.dumps({'version': 1, 'kind': 'note', 'title': 'CLI example', 'tags': [], 'fields': []}))
            result = subprocess.run(['python', '-m', 'cardmaker', 'render', str(source), '--format', 'text'], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(b'CLI example', result.stdout)
            source.write_text('{}')
            result = subprocess.run(['python', '-m', 'cardmaker', 'render', str(source), '--format', 'text'], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'version', result.stderr)

class HTTPTests(unittest.TestCase):
    def test_local_editor_exports_and_security(self):
        from cardmaker.server import make_server
        import threading, http.client, json
        server = make_server('127.0.0.1', 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        conn = http.client.HTTPConnection('127.0.0.1', server.server_port)
        def request(method, path, data=None, headers=None):
            conn.request(method, path, data, headers or {})
            response = conn.getresponse()
            return response.status, response.read()
        try:
            status, body = request('GET', '/')
            self.assertEqual(status, 200)
            self.assertIn(b'Copy text', body)
            card = {'version': 1, 'kind': 'note', 'title': '<script>alert(1)</script>', 'tags': [], 'fields': []}
            payload = json.dumps({'card': card, 'theme': 'dark'})
            for fmt in ('svg', 'png', 'text', 'json'):
                status, body = request('POST', '/api/' + fmt, payload, {'Content-Type': 'application/json'})
                self.assertEqual(status, 200, body)
                self.assertTrue(body)
            self.assertEqual(request('GET', '/../core.py')[0], 404)
            self.assertEqual(request('POST', '/api/svg', payload, {'Origin': 'https://evil.example', 'Content-Type': 'application/json'})[0], 403)
            self.assertEqual(request('POST', '/api/svg', payload, {'Host': 'evil.example', 'Content-Type': 'application/json'})[0], 403)
            self.assertEqual(request('POST', '/api/svg', json.dumps({'card': card, 'theme': '/etc/passwd'}), {'Content-Type': 'application/json'})[0], 400)
            self.assertEqual(request('POST', '/api/svg', '{}', {'Content-Type': 'application/json', 'Content-Length': '999999'})[0], 413)
        finally:
            conn.close()
            server.shutdown()
            server.server_close()
            thread.join()

if __name__ == '__main__': unittest.main()

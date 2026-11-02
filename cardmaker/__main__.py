"""Run from the repository root: python -m cardmaker --help."""
import argparse
import json
import sys
from pathlib import Path
from .core import MAX_BYTES, render


def _cli_seed(value):
    """Decimal CLI tokens become integers; other tokens remain string seeds."""
    try:
        return int(value) if value.lstrip('-').isascii() and value.lstrip('-').isdigit() else value
    except ValueError:
        return value


def _read_json(path):
    with open(path, 'rb') as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Input exceeds 65536-byte limit')
    try:
        return json.loads(raw.decode('utf-8'))
    except RecursionError as exc:
        raise ValueError('Input JSON is too deeply nested') from exc


def main():
    parser = argparse.ArgumentParser(description='Local RPG note cards and connected situation generation. No API required.')
    commands = parser.add_subparsers(dest='command', required=True)
    export = commands.add_parser('render', help='Render a version 1 card JSON file')
    export.add_argument('input', help='JSON file path (UTF-8)')
    export.add_argument('--format', choices=('svg', 'png', 'text'), default='svg')
    export.add_argument('--output', type=Path, help='Output path; omit for stdout (including binary PNG)')
    export.add_argument('--theme', default='dark', help='dark, parchment, or theme JSON path')
    ui = commands.add_parser('ui', help='Serve the local browser editor')
    ui.add_argument('--host', choices=('127.0.0.1', 'localhost'), default='127.0.0.1')
    ui.add_argument('--port', type=int, default=8765, help='Port; 0 chooses an available port')
    generate = commands.add_parser('generate', help='Generate a connected NPC/location proposal')
    generate.add_argument('kind', choices=('npc', 'location'))
    generate.add_argument('--ruleset', choices=('core', 'condensed', 'accelerated', 'neutral'), default='core')
    generate.add_argument('--tier', choices=('mook', 'supporting', 'main'), default='supporting')
    generate.add_argument('--genre', choices=('fantasy', 'noir', 'scifi'), default='fantasy')
    generate.add_argument('--mode', choices=('place', 'scene'), default='place', help='Location mode; fractal is unsupported')
    generate.add_argument('--seed', type=_cli_seed)
    generate.add_argument('--name', help='Lock the requested entity name')
    generate.add_argument('--location-name', help='Lock the connected location name')
    generate.add_argument('--context', help='Preserved unparsed user constraint note; no NLP enforcement')
    project = commands.add_parser('project', help='Project a supported semantic draft into a card view')
    project.add_argument('input', help='Semantic draft JSON, not a generic v1 card')
    reroll = commands.add_parser('reroll', help='Reroll presentation only, preserving the causal core')
    reroll.add_argument('input', help='Semantic draft JSON')
    reroll.add_argument('--seed', type=_cli_seed)
    reroll.add_argument('--group', choices=('presentation',), default='presentation')
    for command in (generate, project, reroll):
        command.add_argument('--audience', choices=('gm', 'public'), default='gm')
        command.add_argument('--detail', choices=('compact', 'full'), default='compact')
        command.add_argument('--format', choices=('json', 'draft', 'text', 'svg', 'png'), default='json')
        command.add_argument('--output', type=Path, help='Output path; otherwise stdout (including binary PNG)')
        command.add_argument('--theme', default='dark', help='dark, parchment, or theme JSON path')
    args = parser.parse_args()
    try:
        if args.command == 'ui':
            from .server import make_server
            server = make_server(args.host, args.port)
            print(f'Cardmaker: http://127.0.0.1:{server.server_port} (Ctrl-C to stop)', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
            return
        if args.command == 'render':
            data = render(_read_json(args.input), args.format, args.theme)
        else:
            from . import generator
            if args.command == 'generate':
                request = {k: getattr(args, k) for k in ('kind', 'ruleset', 'tier', 'genre', 'name', 'location_name', 'context', 'mode')}
                if args.seed is not None:
                    request['seed'] = args.seed
                draft = generator.generate(request)
            else:
                draft = generator.validate_draft(_read_json(args.input))
                if args.command == 'reroll':
                    draft = generator.reroll(draft, args.group, args.seed)
            if args.format == 'draft':
                if args.audience != 'gm':
                    raise ValueError('Semantic drafts contain GM secrets; public draft export is prohibited. Use --format json for a public card.')
                value = generator.validate_draft(draft)
            else:
                value = generator.project(draft, args.audience, args.detail)
            data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8') if args.format in ('json', 'draft') else render(value, args.format, args.theme)
            if args.format == 'draft' and len(data) > MAX_BYTES:
                raise ValueError('Formatted draft exceeds 65536-byte input limit; reduce notes')
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(data)
        else:
            sys.stdout.buffer.write(data)
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(2, f'cardmaker: {exc}\n')


if __name__ == '__main__':
    main()

"""Versioned, data-only card contract and portable renderers."""
import json

KINDS = ('npc', 'location', 'character', 'item', 'faction', 'note')
MAX_BYTES = 65536

def validate(card):
    if not isinstance(card, dict):
        raise ValueError('Card must be a JSON object')
    if type(card.get('version')) is not int or card['version'] != 1:
        raise ValueError('version must be 1')
    if card.get('kind') not in KINDS:
        raise ValueError('kind must be one of: ' + ', '.join(KINDS))
    def string(value, name, required=False):
        if not isinstance(value, str) or (required and not value.strip()):
            raise ValueError(name + ' must be ' + ('a non-empty string' if required else 'a string'))
        if any((ord(c) < 32 and c not in '\n\r\t') or 0xD800 <= ord(c) <= 0xDFFF or ord(c) in (0xFFFE, 0xFFFF) for c in value):
            raise ValueError(name + ' contains unsupported XML characters')
    string(card.get('title'), 'title', True)
    string(card.get('subtitle', ''), 'subtitle')
    if not isinstance(card.get('tags'), list):
        raise ValueError('tags must be a list of strings')
    for tag in card['tags']: string(tag, 'tag')
    if not isinstance(card.get('fields'), list):
        raise ValueError('fields must be a list of label/value objects')
    for field in card['fields']:
        if not isinstance(field, dict): raise ValueError('field must be an object')
        string(field.get('label'), 'field label', True)
        string(field.get('value'), 'field value')
    if len(json.dumps(card, ensure_ascii=False).encode()) > MAX_BYTES:
        raise ValueError('Card exceeds 65536-byte limit')
    return card


def load_theme(theme='dark'):
    from pathlib import Path
    import re
    path = Path(__file__).parent / 'themes' / (theme + '.json') if theme in ('dark', 'parchment') else Path(theme)
    data = json.loads(path.read_text(encoding='utf-8'))
    keys = ('background', 'foreground', 'muted', 'accent')
    if not isinstance(data, dict) or any(not isinstance(data.get(k), str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', data[k]) for k in keys):
        raise ValueError('Theme requires background, foreground, muted, accent as #RRGGBB colors')
    return data


def render(card, format='svg', theme='dark'):
    import io
    import textwrap
    from html import escape
    validate(card)
    if format == 'text':
        rows = [card['title'], card.get('subtitle', ''), card['kind'].upper(), ' · '.join(card['tags'])]
        rows += [f"{f['label']}: {f['value']}" for f in card['fields']]
        return ('\n'.join(r for r in rows if r) + '\n').encode('utf-8')
    colors = load_theme(theme)
    # Conservative fixed-cell layout keeps text inside the card in SVG importers.
    rows = []
    import unicodedata
    def add(text, role='foreground', size=16):
        limit = 32 if size == 24 else 48
        for paragraph in text.split('\n'):
            for line in textwrap.wrap(paragraph.expandtabs(4), width=limit, replace_whitespace=False, drop_whitespace=False) or ['']:
                segment, units = '', 0
                for char in line:
                    weight = 0 if unicodedata.combining(char) else (2 if unicodedata.east_asian_width(char) in ('F', 'W') else 1)
                    if units + weight > limit:
                        rows.append((segment, role, size))
                        segment, units = '', 0
                    segment += char
                    units += weight
                rows.append((segment, role, size))
    add(card['kind'].upper(), 'accent', 16)
    add(card['title'], 'foreground', 24)
    if card.get('subtitle'): add(card['subtitle'], 'muted')
    if card['tags']: add(' · '.join(card['tags']), 'muted')
    for field in card['fields']:
        add('', 'muted')
        add(field['label'], 'accent')
        add(field['value'])
    width, height = 640, 48 + sum(size + 10 for _, _, size in rows)
    if format == 'svg':
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', f'<rect width="100%" height="100%" rx="16" fill="{colors["background"]}"/>']
        y = 24
        for line, role, size in rows:
            y += size
            parts.append(f'<text x="28" y="{y}" fill="{colors[role]}" font-family="DejaVu Sans Mono, monospace" font-size="{size}" xml:space="preserve">{escape(line)}</text>')
            y += 10
        return ('\n'.join(parts) + '</svg>').encode('utf-8')
    if format != 'png': raise ValueError('format must be svg, png, or text')
    if width * height > 16_000_000:
        raise ValueError('PNG exceeds 16-million-pixel safety limit; use SVG or shorten the card')
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise ValueError('PNG requires Pillow: python -m pip install Pillow') from exc
    image = Image.new('RGB', (width, height), colors['background'])
    draw = ImageDraw.Draw(image)
    y = 24
    for line, role, size in rows:
        try: font = ImageFont.truetype('DejaVuSansMono.ttf', size)
        except OSError: font = ImageFont.load_default(size=size)
        draw.text((28, y), line, font=font, fill=colors[role], anchor='lt')
        y += size + 10
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()

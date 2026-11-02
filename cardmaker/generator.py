"""Original, local situation generator. Semantic source is separate from v1 cards."""
import copy
import hashlib
import json
from pathlib import Path
import random
import secrets

VERSION = '1.0.0'
CONTENT = json.loads(Path(__file__).with_name('generator_content.json').read_text(encoding='utf-8'))
DEFAULTS = dict(ruleset='core', tier='supporting', genre='fantasy', mode='place', name=None,
                location_name=None, context=None)


def _text(value, label, maximum=2000, empty=False):
    if not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip()):
        raise ValueError(f'{label} must be a nonempty string of at most {maximum} characters')
    if any((ord(c) < 32 and c not in '\n\r\t') or 0xD800 <= ord(c) <= 0xDFFF or ord(c) in (0xFFFE, 0xFFFF) for c in value):
        raise ValueError(label + ' contains unsupported characters')


def _seed(value):
    if type(value) is int and -(2 ** 53 - 1) <= value <= 2 ** 53 - 1:
        return value
    if isinstance(value, str):
        _text(value, 'seed', 128)
        return value
    raise ValueError('seed must be a JSON-safe integer in range -9007199254740991..9007199254740991 (not bool); use a nonempty string (128 characters max) for larger seeds')


def _request(request):
    if not isinstance(request, dict):
        raise ValueError('request must be an object')
    allowed = set(DEFAULTS) | {'kind', 'seed'}
    if set(request) - allowed:
        raise ValueError('unknown request keys: ' + ', '.join(str(k) for k in set(request) - allowed))
    req = dict(DEFAULTS, **request)
    for key, values in dict(kind=('npc', 'location'), ruleset=('neutral', 'core', 'condensed', 'accelerated'),
                            tier=('mook', 'supporting', 'main'), genre=('fantasy', 'noir', 'scifi'),
                            mode=('place', 'scene')).items():
        if not isinstance(req.get(key), str) or req[key] not in values:
            raise ValueError(key + ' must be one of ' + ', '.join(values) + ('; fractal mode is unsupported' if key == 'mode' else ''))
    if 'seed' in req:
        _seed(req['seed'])
    for key in ('name', 'location_name', 'context'):
        if req[key] is not None:
            _text(req[key], key, 2000 if key == 'context' else 120, empty=key == 'context')
    if req['kind'] == 'location' and req['name'] and req['location_name'] and req['name'] != req['location_name']:
        raise ValueError('name and location_name conflict for requested location')
    return req


def _aspect(text, scope='character', category='other', help_example=None, complication=None):
    return dict(text=text, scope=scope, category=category,
                help=help_example or 'Draw on this established connection or expertise when creating an advantage.',
                complication=complication or 'An obligation attached to this truth demands attention at an inconvenient time.')


def _durability(ruleset, tier, ratings, recipe='Fair'):
    """Preset box capacities, not HP; consequences are empty harm-aspect slots."""
    slots = [dict(severity=s, capacity=c, domain='any', aspect=None)
             for s, c in [('mild', 2), ('moderate', 4), ('severe', 6)]][:3 if tier == 'main' else 1]
    policy = 'multiple_boxes_per_hit' if ruleset == 'condensed' else 'one_box_per_hit'
    if tier == 'mook':
        capacities = {'Average': [], 'Fair': [1], 'Good': [1, 2]}[recipe] if ruleset == 'core' else [1, 1] if ruleset == 'condensed' else [1, 2]
        return [dict(domain='unified', capacities=capacities, mark_policy=policy, derivation='native lightweight NPC preset')], []
    if ruleset == 'accelerated':
        return [dict(domain='unified', capacities=[1, 2, 3] if tier == 'main' else [1, 2],
                     mark_policy=policy, derivation='FAE fixed track; reduced for project supporting preset')], slots
    tracks = []
    for domain, skill in [('physical', 'Physique'), ('mental', 'Will')]:
        rating = ratings.get(skill, 0)
        count = (2 if rating == 0 else 3 if rating < 3 else 4) if ruleset == 'core' else (3 if rating == 0 else 4 if rating < 3 else 6)
        tracks.append(dict(domain=domain, capacities=list(range(1, count + 1)) if ruleset == 'core' else [1] * count,
                           mark_policy=policy, derivation=f'{ruleset}: {skill} {rating:+d}'))
        if rating >= 5:
            slots.append(dict(severity='mild', capacity=2, domain=domain, aspect=None))
    return tracks, slots


def _mechanics(req, pack, rng):
    ruleset, tier = req['ruleset'], req['tier']
    if ruleset == 'neutral':
        return None
    recipe = rng.choice(['Average', 'Fair', 'Good']) if ruleset == 'core' and tier == 'mook' else 'default'
    native = {'core': {'mook': 'nameless', 'supporting': 'supporting', 'main': 'main'},
              'condensed': {'mook': 'minor', 'supporting': 'reduced major — project convenience', 'main': 'major'},
              'accelerated': {'mook': 'mook', 'supporting': 'reduced important NPC — project convenience', 'main': 'important NPC'}}[ruleset][tier]
    if ruleset == 'accelerated':
        model = 'competence_bands' if tier == 'mook' else 'approaches'
        ratings = dict(zip([pack['strength'], pack['weakness']], [2, -2])) if tier == 'mook' else dict(zip(pack['approaches'], [3, 2, 2, 1, 1, 0] if tier == 'main' else [2, 1, 1, 0, 0, 0]))
    else:
        model = 'skills'
        skills = [s if s != 'Lore' or ruleset != 'condensed' else 'Academics' for s in pack['skills']]
        shape = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1] if tier == 'main' else [4, 3, 2, 1] if tier == 'supporting' and ruleset == 'core' else [3, 2, 1, 1] if tier == 'supporting' else {'Average': [1, 1], 'Fair': [2, 1, 1], 'Good': [3, 2, 1, 1]}.get(recipe, [2, 1])
        ratings = dict(zip(skills, shape))
    aspects = [_aspect(pack[key], category=category) for key, category in
               [('concept', 'high_concept'), ('trouble', 'trouble'), ('bond', 'relationship'), ('method', 'method'), ('hope', 'aspiration')]][:{'mook': 2, 'supporting': 3, 'main': 5}[tier]]
    aspects[0]['help'] = 'Use local expertise to work with the resource: ' + pack['resource'] + '.'
    aspects[0]['complication'] = pack['obstacle']
    aspects[1]['help'] = 'Recognize competing claims and negotiate an alternative to force.'
    aspects[1]['complication'] = pack['boundary']
    if len(aspects) > 2:
        aspects[2]['help'] = 'Ask ' + pack['faction'] + ' for access, witnesses or a temporary guarantee.'
        aspects[2]['complication'] = pack['faction'] + ' demands priority access to ' + pack['resource'] + ' before honoring the connection.'
    if len(aspects) > 3:
        aspects[3]['help'] = 'Apply an established verification procedure to ' + pack['resource'] + ' before committing to a risky action.'
        aspects[3]['complication'] = 'Verification costs time: ' + pack['pressure']
        aspects[4]['help'] = 'Propose shared use of ' + pack['resource'] + ' as common ground for negotiation.'
        aspects[4]['complication'] = 'Pursuing this ideal can force a choice: ' + pack['boundary']
    stress, consequences = _durability(ruleset, tier, ratings, recipe if recipe != 'default' else 'Fair')
    best = next(iter(ratings))
    circumstance = ('while consulting witnesses about the maintenance or routing of ' if best == 'Contacts' else 'while personally inspecting the mechanisms or records that control ') + pack['resource']
    stunt = dict(name='Read the Working System', competency=best, action='create_advantage',
                 circumstance=circumstance,
                 effect='Add +2 to create an advantage identifying a fault or bottleneck; not to attacks or general persuasion.',
                 limit='Only this narrow inspection action; no free invoke unless the action earns one.', table_review=True)
    return dict(ruleset=ruleset, native_tier=native, recipe=recipe,
                competencies=dict(model=model, ratings=ratings, default=0), aspects=aspects,
                stress=stress, consequences=consequences, stunts=[] if tier == 'mook' else [stunt],
                extreme_option='Core last resort: replace a non-high-concept aspect; not a reusable consequence slot.' if ruleset == 'core' and tier == 'main' else 'Not enabled',
                assumptions='Project starting opposition preset; PC context unknown; not encounter-balanced. No private NPC fate pool.')


def _scene(req, pack, npc_id, loc_id):
    if req['mode'] == 'place':
        return None
    ids = [loc_id + ':zone:' + str(i) for i in range(1, 4)]
    aspects = [] if req['ruleset'] == 'neutral' else [
        _aspect(pack['pressure'], 'scene', 'pressure', 'Use the deadline to bargain for immediate access.', 'Delay gives the claimants time to seize control.'),
        _aspect('Access to ' + pack['resource'], 'scene', 'resource', 'Use the available resource as leverage or a practical tool.', 'Its competing owners demand a share before helping.'),
        _aspect(pack['warning'], 'scene', 'warning', 'Follow the warning to locate the threatened mechanism or route.', pack['danger'])]
    return dict(participants=[npc_id], stakes='Who controls ' + pack['resource'] + '?',
                zones=[dict(id=i, name=n) for i, n in zip(ids, pack['zones'])],
                edges=[dict(**{'from': ids[i], 'to': ids[i + 1]}, note=pack['edge_notes'][i]) for i in range(2)],
                aspects=aspects, free_invokes=0,
                obstacle=dict(kind='passive', task='Work around the obstruction: ' + pack['warning'],
                              difficulty=None if req['ruleset'] == 'neutral' else 2,
                              assumption='Illustrative sample difficulty +2, not a mandatory roll or encounter balance; adjust to fiction and PCs.' if req['ruleset'] != 'neutral' else 'Narrative obstacle only; no numeric mechanics.',
                              failure=pack['danger'], counterplay=pack['counterplay']))


def generate(request):
    """Generate one connected proposal, selecting the requested kind at projection."""
    req = _request(request)
    seed = req.setdefault('seed', secrets.randbits(53))
    rng = random.Random(seed)
    pack = copy.deepcopy(rng.choice([p for p in CONTENT['packs'] if p['genre'] == req['genre']]))
    npc_name = req['name'] if req['kind'] == 'npc' and req['name'] else pack['npc_name']
    loc_name = req['location_name'] or (req['name'] if req['kind'] == 'location' else None) or pack['location_name']
    if npc_name.strip().casefold() == loc_name.strip().casefold():
        raise ValueError('NPC and location display names must differ')
    token = hashlib.sha256((str(seed) + ':' + pack['id']).encode()).hexdigest()[:12]
    npc_id, loc_id = 'npc:' + token, 'location:' + token
    secret = dict(fact=pack['secret'], channels=pack['channels'], meaning=pack['meaning'])
    npc = dict(id=npc_id, name=npc_name, location_ref=loc_id,
               public=dict(role=pack['role'], appearance=pack['appearance'], voice=pack['voice'], offer=pack['offer']),
               gm={k: pack[k] for k in ('objective', 'obstacle', 'boundary')}, mechanics=_mechanics(req, pack, rng))
    npc['gm'].update(relationship=pack['relationship'].format(npc=npc_name, location=loc_name),
                     secret=secret, concession='Yield control of the resource rather than endanger bystanders.')
    loc = dict(id=loc_id, name=loc_name, npc_refs=[npc_id], mode=req['mode'],
               public={k: pack[k] for k in ('purpose', 'sensory', 'features', 'warning')},
               gm={k: pack[k] for k in ('pressure', 'trigger', 'danger', 'counterplay', 'opportunity', 'choices')}, scene=_scene(req, pack, npc_id, loc_id))
    return dict(version=1, request=req,
                provenance=dict(generator_version=VERSION, content_version=CONTENT['version'], seed=seed,
                                presentation_seed=seed, presentation_revision=0,
                                bundle_id=pack['id'], origin='generated proposal; not campaign canon',
                                context_policy='User context is an unparsed constraint note; no NLP enforcement'),
                situation=dict(resource=pack['resource'], faction=pack['faction'], npc_ref=npc_id, location_ref=loc_id),
                npc=npc, location=loc, canon_notes=[])


SCHEMA = json.loads(Path(__file__).with_name('generation_schema.json').read_text(encoding='utf-8'))


def _check_schema(value, schema, path='draft'):
    """Validate the small JSON Schema subset used by our bundled contract (stdlib)."""
    if '$ref' in schema:
        if schema['$ref'] == '#/$defs/seed':
            try:
                _seed(value)
            except ValueError as exc:
                raise ValueError(path + ': ' + str(exc)) from None
        return _check_schema(value, SCHEMA['$defs'][schema['$ref'].rsplit('/', 1)[1]], path)
    if 'anyOf' in schema:
        for option in schema['anyOf']:
            try:
                _check_schema(value, option, path)
                return
            except ValueError:
                pass
        raise ValueError(path + ' has an unsupported value or shape')
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        raise ValueError(path + ' does not match the supported constant')
    if 'enum' in schema and not any(type(value) is type(v) and value == v for v in schema['enum']):
        raise ValueError(path + ' has an unsupported enum value')
    kind = schema.get('type')
    valid = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str), 'integer': type(value) is int,
             'null': value is None}
    if kind and not valid[kind]:
        raise ValueError(path + ' must be ' + kind)
    if kind == 'object':
        props = schema.get('properties', {})
        if any(k not in value for k in schema.get('required', [])):
            raise ValueError(path + ' is missing required keys')
        if not schema.get('minProperties', 0) <= len(value) <= schema.get('maxProperties', 100):
            raise ValueError(path + ' has an invalid property count')
        for key, entry in value.items():
            _text(key, path + ' key', 120)
            sub = props.get(key, schema.get('additionalProperties', {}))
            if sub is False:
                raise ValueError(path + ' has unknown key ' + key)
            _check_schema(entry, sub, path + '.' + key)
    elif kind == 'array':
        if not schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', 100):
            raise ValueError(path + ' has an invalid item count')
        for entry in value:
            _check_schema(entry, schema['items'], path + '[]')
    elif kind == 'string':
        _text(value, path, schema.get('maxLength', 2000), empty=schema.get('minLength', 1) == 0)
    elif kind == 'integer':
        if not schema.get('minimum', -(2 ** 63)) <= value <= schema.get('maximum', 2 ** 63 - 1):
            raise ValueError(path + ' is out of range')


def validate_draft(draft):
    """Validate only this known generator/source schema, not arbitrary authored Fate hacks."""
    _check_schema(draft, SCHEMA)
    if len(json.dumps(draft, ensure_ascii=False).encode('utf-8')) > 65536:
        raise ValueError('Draft exceeds 65536-byte limit')
    req = _request(draft['request'])
    expected = generate(req)
    if any(draft['provenance'][k] != v for k, v in expected['provenance'].items()
           if k not in ('presentation_seed', 'presentation_revision')):
        raise ValueError('Unsupported or inconsistent provenance/seed/content bundle')
    npc, loc = draft['npc'], draft['location']
    if npc['name'].strip().casefold() == loc['name'].strip().casefold():
        raise ValueError('NPC and location names must differ')
    for key in ('npc', 'location'):
        if draft[key]['id'] != expected[key]['id']:
            raise ValueError('Entity IDs must match their original source')
    if npc['location_ref'] != loc['id'] or loc['npc_refs'] != [npc['id']]:
        raise ValueError('Broken entity references')
    if draft['situation']['npc_ref'] != npc['id'] or draft['situation']['location_ref'] != loc['id']:
        raise ValueError('Broken situation references')
    if loc['mode'] != req['mode']:
        raise ValueError('Location mode does not match request')
    if req['name'] and draft[req['kind']]['name'] != req['name']:
        raise ValueError('Requested name lock changed')
    if req['location_name'] and loc['name'] != req['location_name']:
        raise ValueError('Location name lock changed')
    if npc['name'] not in npc['gm']['relationship'] or loc['name'] not in npc['gm']['relationship']:
        raise ValueError('Relationship must identify both linked display names')
    mechanics, known = npc['mechanics'], expected['npc']['mechanics']
    if (mechanics is None) != (known is None):
        raise ValueError('Neutral mode must be mechanically neutral')
    if mechanics:
        for key in known:
            if key != 'aspects' and mechanics[key] != known[key]:
                raise ValueError('Unsupported rules preset change: ' + key)
        if len(mechanics['aspects']) != len(known['aspects']) or any(a['scope'] != 'character' for a in mechanics['aspects']):
            raise ValueError('Invalid character aspect scope/count')
    scene, known_scene = loc['scene'], expected['location']['scene']
    if (scene is None) != (known_scene is None):
        raise ValueError('Places are statless; scenes require the supported scene structure')
    if scene:
        if scene['participants'] != [npc['id']]:
            raise ValueError('Broken scene participant references')
        ids = [z['id'] for z in scene['zones']]
        if ids != [z['id'] for z in known_scene['zones']]:
            raise ValueError('Zone IDs are missing, duplicated or changed')
        if len({z['name'].casefold() for z in scene['zones']}) != 3:
            raise ValueError('Zone names must differ')
        if [(e['from'], e['to']) for e in scene['edges']] != [(e['from'], e['to']) for e in known_scene['edges']]:
            raise ValueError('Broken or disconnected zone edges')
        if len(scene['aspects']) != len(known_scene['aspects']) or any(a['scope'] != 'scene' for a in scene['aspects']):
            raise ValueError('Invalid scene aspect scope/count')
        if scene['obstacle']['difficulty'] != known_scene['obstacle']['difficulty']:
            raise ValueError('Unsupported scene difficulty for rules profile')
    return draft


def reroll(draft, group='presentation', seed=None):
    """Change delivery/emphasis only; never redraw names, source, mechanics or causal facts."""
    if not isinstance(group, str) or group != 'presentation':
        raise ValueError('Only presentation rerolls are supported; mechanics and situation rerolls are unsupported')
    validate_draft(draft)
    chosen = secrets.randbits(53) if seed is None else _seed(seed)
    rng = random.Random(chosen)
    result = copy.deepcopy(draft)
    # Reframe existing prose instead of adding unrelated traits or changing established facts.
    voice = draft['npc']['public']['voice']
    prefixes = ['Delivery — short clauses: ', 'Delivery — measured pauses: ', 'Delivery — one thought at a time: ']
    for prefix in prefixes:
        if voice.startswith(prefix):
            voice = voice[len(prefix):]
            break
    alternatives = [prefix + voice for prefix in prefixes if prefix + voice != draft['npc']['public']['voice']]
    result['npc']['public']['voice'] = rng.choice(alternatives)
    appearance = draft['npc']['public']['appearance']
    labels = ['Visible detail: ', 'First impression: ', 'Notice first: ']
    for label in labels:
        if appearance.startswith(label):
            appearance = appearance[len(label):]
            break
    result['npc']['public']['appearance'] = rng.choice([label + appearance for label in labels if label + appearance != draft['npc']['public']['appearance']])
    rng.shuffle(result['location']['public']['sensory'])
    result['provenance']['presentation_seed'] = chosen
    result['provenance']['presentation_revision'] += 1
    return validate_draft(result)


def project(draft, audience='gm', detail='compact'):
    """Project a strict visibility allowlist into a metadata-free v1 card."""
    from .core import validate
    if not isinstance(audience, str) or audience not in ('gm', 'public'):
        raise ValueError('audience must be gm or public')
    if not isinstance(detail, str) or detail not in ('compact', 'full'):
        raise ValueError('detail must be compact or full')
    validate_draft(draft)
    req, npc, loc = draft['request'], draft['npc'], draft['location']
    fields = []
    def add(label, value):
        fields.append(dict(label=label, value=value))
    def aspects(items):
        for aspect in items:
            value = aspect['text']
            if detail == 'full':
                value += '\nHelp: ' + aspect['help'] + '\nComplication: ' + aspect['complication']
            add('Aspect (' + aspect['scope'] + ')', value)
    if req['kind'] == 'npc':
        for key in ('appearance', 'voice', 'offer'):
            add(key.title(), npc['public'][key])
        add('At', loc['name'])
        if audience == 'gm':
            for key in ('objective', 'obstacle', 'boundary', 'relationship'):
                add(key.title(), npc['gm'][key])
            mechanics = npc['mechanics']
            if mechanics:
                add('Rules preset', req['ruleset'] + ' / ' + mechanics['native_tier'] + (' / ' + mechanics['recipe'] if mechanics['recipe'] != 'default' else ''))
                aspects(mechanics['aspects'])
                comp = mechanics['competencies']
                add(comp['model'].replace('_', ' ').title(), ', '.join(k + f' {v:+d}' for k, v in comp['ratings'].items()) + '; unlisted +0')
                add('Stress (box capacities, not HP)', '; '.join(t['domain'] + ' [' + ','.join(map(str, t['capacities'])) + '] ' + t['mark_policy'] for t in mechanics['stress']))
                add('Consequences (empty slots)', '; '.join(s['severity'] + f" {s['capacity']} ({s['domain']}) [empty]" for s in mechanics['consequences']) or 'None')
                for stunt in mechanics['stunts']:
                    add('Stunt — table review', stunt['name'] + ': ' + stunt['competency'] + ' / ' + stunt['action'] + ' ' + stunt['circumstance'] + '. ' + stunt['effect'] + (' ' + stunt['limit'] if detail == 'full' else ''))
                if detail == 'full':
                    add('Stress derivation', '; '.join(t['derivation'] for t in mechanics['stress']))
                    add('Rules boundaries', mechanics['assumptions'] + ' ' + mechanics['extreme_option'] + ' Aspects are fictional truths, not automatic +2 bonuses. Use the selected ruleset for recovery.')
            add('GM secret', npc['gm']['secret']['fact'])
            if detail == 'full':
                add('Concession option', npc['gm']['concession'])
    else:
        add('Purpose', loc['public']['purpose'])
        add('Sensory anchors', ' / '.join(loc['public']['sensory']))
        add('Face', npc['name'] + ' — ' + npc['public']['role'])
        for feature in loc['public']['features']:
            add(feature['name'], feature['interaction'])
        add('Warning', loc['public']['warning'])
        if audience == 'gm':
            for key in ('pressure', 'trigger', 'danger', 'counterplay', 'opportunity'):
                add(key.title(), loc['gm'][key])
            add('Open choices', ' / '.join(loc['gm']['choices']))
            scene = loc['scene']
            if scene:
                add('Scene stakes', scene['stakes'])
                names = {z['id']: z['name'] for z in scene['zones']}
                add('Zones / connections', '; '.join(names[e['from']] + ' ↔ ' + names[e['to']] + ': ' + e['note'] for e in scene['edges']))
                aspects(scene['aspects'])
                obstacle = scene['obstacle']
                add('Passive obstacle (sample)', obstacle['task'] + (f" Difficulty +{obstacle['difficulty']}." if obstacle['difficulty'] is not None else '') + ' ' + obstacle['assumption'])
                if detail == 'full':
                    add('Scene setup policy', 'Zero free invokes assigned by this generator; GM may award them for established preparation. Roll only if interesting opposition exists; zones and aspect counts are project defaults.')
            else:
                add('Place policy', 'Statless reference place; no skills, stress, consequences or mandatory aspects.')
            if detail == 'full':
                add('Linked NPC objective', npc['gm']['objective'])
                add('GM secret', npc['gm']['secret']['fact'])
    if audience == 'gm' and detail == 'full':
        add('Discovery options (not mandatory gates)', ' / '.join(npc['gm']['secret']['channels']))
        add('Why the secret matters', npc['gm']['secret']['meaning'])
        if req['context'] is not None:
            add('User context — unparsed constraint note', req['context'])
        for note in draft['canon_notes']:
            add('Preserved canon note (GM)', note)
        p = draft['provenance']
        add('Proposal source', f"Generator {p['generator_version']}; original content {p['content_version']}; bundle {p['bundle_id']}; seed {p['seed']}. Not campaign canon; no NLP constraint enforcement.")
    entity = draft[req['kind']]
    subtitle = npc['public']['role'] if req['kind'] == 'npc' else 'Place reference' if req['mode'] == 'place' else 'Scene setup'
    return validate(dict(version=1, kind=req['kind'], title=entity['name'], subtitle=subtitle,
                         tags=[req['genre'], req['ruleset'], audience, 'generated proposal'], fields=fields))

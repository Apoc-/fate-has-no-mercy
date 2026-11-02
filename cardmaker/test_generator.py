"""Vertical generator contract and CLI regression tests (stdlib unittest)."""
import copy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest


class GeneratorTests(unittest.TestCase):
    def engine(self):
        from . import generator
        return generator

    def test_seed_contract_rejects_unsafe_numbers_before_provenance(self):
        g = self.engine()
        from .server import check_seed
        safe = 2 ** 53 - 1
        draft = g.generate({'kind': 'npc', 'seed': 42})
        for seed in (safe + 1, -safe - 1, 2 ** 63 - 1, -(2 ** 63), True, 1.5):
            for operation in (g._seed, check_seed,
                              lambda value: g.generate({'kind': 'npc', 'seed': value}),
                              lambda value: g.reroll(draft, seed=value)):
                with self.subTest(seed=seed, operation=operation), self.assertRaisesRegex(ValueError, 'safe integer.*string'):
                    operation(seed)
            for path in (('request', 'seed'), ('provenance', 'seed'), ('provenance', 'presentation_seed')):
                bad = copy.deepcopy(draft)
                bad[path[0]][path[1]] = seed
                # Seed/schema errors must precede misleading provenance/ID errors.
                with self.subTest(seed=seed, path=path), self.assertRaisesRegex(ValueError, 'safe integer.*string'):
                    g.validate_draft(bad)
        for seed in (-safe, -42, 0, 42, safe, 'abc', str(2 ** 63 - 1), '0' * 128, '  arbitrary seed  '):
            with self.subTest(seed=seed):
                self.assertEqual(g._seed(seed), seed)
                check_seed(seed)
                generated = g.generate({'kind': 'npc', 'seed': seed})
                self.assertIs(type(generated['provenance']['seed']), type(seed))
                self.assertEqual(g.validate_draft(generated), generated)
                self.assertEqual(g.reroll(generated, seed=seed)['provenance']['presentation_seed'], seed)
        schema = json.loads(Path(g.__file__).with_name('generation_schema.json').read_text())
        for definition, key in (('request', 'seed'), ('provenance', 'seed'), ('provenance', 'presentation_seed')):
            contract = schema['$defs'][definition]['properties'][key]
            if '$ref' in contract:
                contract = schema['$defs'][contract['$ref'].rsplit('/', 1)[1]]
            numeric = next(option for option in contract['anyOf'] if option['type'] == 'integer')
            self.assertEqual((numeric['minimum'], numeric['maximum']), (-safe, safe))

    def test_existing_integer_and_string_seed_outputs_are_unchanged(self):
        g = self.engine()
        seeds = [-(2 ** 53 - 1), -42, 0, 42, 2 ** 53 - 1,
                 'abc', str(2 ** 63 - 1), '0009', '  arbitrary seed  ']
        results = []
        for seed in seeds:
            source = g.generate({'kind': 'npc', 'mode': 'scene', 'seed': seed})
            results.append([source, g.reroll(source, seed=seed)])
        # Captured from the original generator before the precision fix.
        digest = hashlib.sha256(json.dumps(results, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(digest, '8ff0c897359c7777bb70c8573a7d9c90246a5e6725e7f9420337f3959dbfa85f')

    def test_connected_deterministic_neutral_draft(self):
        g = self.engine()
        request = dict(kind='npc', ruleset='neutral', seed=42, name='Óren', location_name='The Lock')
        state = random.getstate()
        draft = g.generate(request)
        self.assertEqual(draft, g.generate(request))
        self.assertEqual(random.getstate(), state)
        self.assertEqual(draft['npc']['name'], 'Óren')
        self.assertEqual(draft['location']['name'], 'The Lock')
        self.assertEqual(draft['npc']['location_ref'], draft['location']['id'])
        self.assertEqual(draft['location']['npc_refs'], [draft['npc']['id']])
        self.assertIsNone(draft['npc']['mechanics'])
        self.assertEqual(draft['provenance']['seed'], 42)
        self.assertTrue(draft['npc']['gm']['objective'])
        self.assertEqual(len(draft['npc']['gm']['secret']['channels']), 3)
        self.assertTrue(draft['location']['public']['features'][0]['interaction'])

    def test_request_validation_names_context_defaults(self):
        g = self.engine()
        for payload in (None, [], {}, {'kind': []}, {'kind': 'npc', 'seed': True},
                        {'kind': 'npc', 'seed': 1.2}, {'kind': 'npc', 'seed': ''},
                        {'kind': 'npc', 'ruleset': {}}, {'kind': 'npc', 'tier': []},
                        {'kind': 'npc', 'genre': None}, {'kind': 'location', 'mode': 'fractal'},
                        {'kind': 'npc', 'unknown': 1}, {'kind': 'npc', 'context': 'x' * 2001},
                        {'kind': 'npc', 'name': '\u0001'}, {'kind': 'npc', 'name': '  '},
                        {'kind': 'npc', 'name': 'Same', 'location_name': 'same'},
                        {'kind': 'location', 'name': 'One', 'location_name': 'Other'}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                g.generate(payload)
        note = '  Existing canon.\nDo not reinterpret this!  '
        d = g.generate(dict(kind='location', name='Custom Quay', context=note, seed='abc'))
        self.assertEqual(d['request']['context'], note)
        self.assertEqual(d['request']['ruleset'], 'core')
        self.assertEqual(d['location']['name'], 'Custom Quay')
        self.assertIn('Custom Quay', d['npc']['gm']['relationship'])
        self.assertIn('unparsed', d['provenance']['context_policy'])
        self.assertIsInstance(g.generate({'kind': 'npc'})['provenance']['seed'], int)

    def test_rules_profiles_native_tiers_and_durability(self):
        g = self.engine()
        for ruleset in ('core', 'condensed', 'accelerated'):
            for tier in ('mook', 'supporting', 'main'):
                d = g.generate(dict(kind='npc', seed=2, ruleset=ruleset, tier=tier))
                m = d['npc']['mechanics']
                self.assertEqual(m['ruleset'], ruleset)
                self.assertTrue(m['native_tier'])
                self.assertNotIn('fate_points', m)
                self.assertEqual(len(m['aspects']), {'mook': 2, 'supporting': 3, 'main': 5}[tier])
                for aspect in m['aspects']:
                    self.assertTrue(aspect['help'])
                    self.assertTrue(aspect['complication'])
                for slot in m['consequences']:
                    self.assertIsNone(slot['aspect'])
                if tier == 'mook':
                    self.assertEqual(m['consequences'], [])
                else:
                    self.assertTrue(m['stunts'][0]['table_review'])
                    self.assertEqual(m['stunts'][0]['action'], 'create_advantage')
                if tier == 'supporting' and ruleset != 'core':
                    self.assertIn('project convenience', m['native_tier'])
                if tier == 'main':
                    self.assertEqual([s['capacity'] for s in m['consequences']], [2, 4, 6])
                    if ruleset == 'accelerated':
                        self.assertEqual(sorted(m['competencies']['ratings'].values()), [0, 1, 1, 2, 2, 3])
                        self.assertEqual(m['competencies']['model'], 'approaches')
                    else:
                        self.assertEqual(sorted(m['competencies']['ratings'].values()), [1, 1, 1, 1, 2, 2, 2, 3, 3, 4])
                        self.assertEqual(m['competencies']['model'], 'skills')
        c = g.generate(dict(kind='npc', ruleset='condensed', tier='main', seed=2))
        self.assertIn('Academics', c['npc']['mechanics']['competencies']['ratings'])
        for rating in (0, 1, 2, 3, 4, 5, 6):
            for ruleset in ('core', 'condensed'):
                tracks, slots = g._durability(ruleset, 'main', {'Physique': rating, 'Will': rating})
                count = (2 if rating == 0 else 3 if rating < 3 else 4) if ruleset == 'core' else (3 if rating == 0 else 4 if rating < 3 else 6)
                self.assertEqual([t['capacities'] for t in tracks], [list(range(1, count + 1)) if ruleset == 'core' else [1] * count] * 2)
                self.assertEqual(tracks[0]['mark_policy'], 'one_box_per_hit' if ruleset == 'core' else 'multiple_boxes_per_hit')
                self.assertEqual(len(slots), 5 if rating >= 5 else 3)
        recipes = set()
        for seed in range(30):
            m = g.generate(dict(kind='npc', tier='mook', seed=seed))['npc']['mechanics']
            recipes.add(m['recipe'])
            expected = {'Average': ([1, 1], []), 'Fair': ([2, 1, 1], [1]), 'Good': ([3, 2, 1, 1], [1, 2])}[m['recipe']]
            self.assertEqual(list(m['competencies']['ratings'].values()), expected[0])
            self.assertEqual(m['stress'][0]['capacities'], expected[1])
        self.assertEqual(recipes, {'Average', 'Fair', 'Good'})
        fae = g.generate(dict(kind='npc', ruleset='accelerated', tier='mook', seed=2))['npc']['mechanics']
        self.assertEqual(sorted(fae['competencies']['ratings'].values()), [-2, 2])
        self.assertEqual(fae['competencies']['default'], 0)

    def test_genre_bundles_scene_graph_and_360_seed_coherence(self):
        g = self.engine()
        for genre in ('fantasy', 'noir', 'scifi'):
            bundles = set()
            for seed in range(120):
                d = g.generate(dict(kind='location', ruleset='neutral', genre=genre, seed=seed, mode='scene'))
                bundles.add(d['provenance']['bundle_id'])
                self.assertTrue(d['provenance']['bundle_id'].startswith(genre + '-'))
                scene = d['location']['scene']
                self.assertEqual(len(scene['zones']), 3)
                ids = {z['id'] for z in scene['zones']}
                linked = set()
                for edge in scene['edges']:
                    self.assertIn(edge['from'], ids)
                    self.assertIn(edge['to'], ids)
                    linked.update([edge['from'], edge['to']])
                self.assertEqual(linked, ids)
                self.assertEqual(scene['participants'], [d['npc']['id']])
                self.assertEqual(scene['obstacle']['difficulty'], None)
                self.assertEqual(scene['aspects'], [])
                self.assertEqual(len(d['location']['public']['sensory']), 2)
                self.assertTrue(d['location']['gm']['counterplay'])
                self.assertEqual(len(d['location']['gm']['choices']), 3)
                self.assertNotIn('{npc}', json.dumps(d))
                self.assertNotIn('{location}', json.dumps(d))
            self.assertGreaterEqual(len(bundles), 3)
        d = g.generate(dict(kind='location', mode='scene', seed=4))
        scene = d['location']['scene']
        self.assertEqual(len(scene['aspects']), 3)
        self.assertEqual({a['scope'] for a in scene['aspects']}, {'scene'})
        self.assertEqual(scene['obstacle']['difficulty'], 2)
        self.assertIn('sample', scene['obstacle']['assumption'])
        self.assertEqual(scene['free_invokes'], 0)
        d = g.generate(dict(kind='location', mode='place', seed=4))
        self.assertIsNone(d['location']['scene'])
        for key in ('skills', 'stress', 'consequences', 'mechanics', 'zones'):
            self.assertNotIn(key, d['location'])

    def test_validate_draft_rejects_bad_structure_refs_rules_metadata(self):
        g = self.engine()
        d = g.generate(dict(kind='npc', seed=7, mode='scene'))
        self.assertEqual(g.validate_draft(d), d)
        mutations = [
            (['version'], True), (['request', 'seed'], True),
            (['provenance', 'generator_version'], 'future'),
            (['provenance', 'content_version'], []), (['provenance', 'seed'], 'other'),
            (['provenance', 'bundle_id'], 'noir-missing'),
            (['npc', 'location_ref'], 'missing'), (['location', 'npc_refs'], ['missing']),
            (['npc', 'gm', 'objective'], ''), (['npc', 'name'], d['location']['name']),
            (['npc', 'gm', 'secret', 'channels'], ['one']),
            (['npc', 'mechanics', 'ruleset'], 'condensed'),
            (['npc', 'mechanics', 'competencies', 'ratings', 'Physique'], True),
            (['npc', 'mechanics', 'stress', 0, 'capacities'], [1, 2, 99]),
            (['npc', 'mechanics', 'stress', 0, 'mark_policy'], 'multiple_boxes_per_hit'),
            (['npc', 'mechanics', 'consequences', 0, 'aspect'], 'Prewritten wound'),
            (['location', 'scene', 'edges', 0, 'to'], 'missing'),
            (['location', 'scene', 'zones', 1, 'id'], d['location']['scene']['zones'][0]['id']),
            (['location', 'scene', 'obstacle', 'difficulty'], 'easy'),
            (['canon_notes'], ['x' * 2001]),
        ]
        for path, value in mutations:
            bad = copy.deepcopy(d)
            obj = bad
            for key in path[:-1]:
                obj = obj[key]
            obj[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                g.validate_draft(bad)
        for bad in (None, [], {}, {'version': 1}, dict(d, extra='secret extension')):
            with self.assertRaises(ValueError):
                g.validate_draft(bad)
        bad = copy.deepcopy(d)
        del bad['npc']['gm']['obstacle']
        with self.assertRaises(ValueError):
            g.validate_draft(bad)
        locked = g.generate(dict(kind='npc', name='Locked', seed=7))
        locked['npc']['name'] = 'Changed'
        with self.assertRaises(ValueError):
            g.validate_draft(locked)
        self.assertEqual(json.loads(Path(g.__file__).with_name('generation_schema.json').read_text())['$defs']['request']['additionalProperties'], False)

    def test_projection_v1_public_allowlist_and_gm_detail(self):
        g = self.engine()
        from .core import validate
        for kind in ('npc', 'location'):
            d = g.generate(dict(kind=kind, mode='scene', seed=8, context='PRIVATE CONTEXT'))
            d['canon_notes'] = ['PRIVATE CANON']
            d['npc']['gm']['objective'] = 'PRIVATE OBJECTIVE'
            d['npc']['gm']['secret']['fact'] = 'PRIVATE SECRET'
            d['npc']['gm']['secret']['channels'] = ['PRIVATE CLUE A', 'PRIVATE CLUE B', 'PRIVATE CLUE C']
            d['npc']['mechanics']['aspects'][0]['help'] = 'PRIVATE ASPECT GUIDANCE'
            for detail in ('compact', 'full'):
                card = g.project(d, audience='public', detail=detail)
                validate(card)
                self.assertEqual(set(card), {'version', 'kind', 'title', 'subtitle', 'tags', 'fields'})
                self.assertNotIn('PRIVATE', json.dumps(card))
                self.assertNotIn('provenance', json.dumps(card))
                self.assertEqual(card['kind'], kind)
            compact = g.project(d)
            full = g.project(d, detail='full')
            self.assertGreater(len(json.dumps(full)), len(json.dumps(compact)))
            self.assertIn('PRIVATE SECRET', json.dumps(full))
            self.assertIn('PRIVATE CLUE A', json.dumps(full))
            self.assertIn('PRIVATE CONTEXT', json.dumps(full))
            self.assertIn('unparsed', json.dumps(full))
            self.assertIn('PRIVATE CANON', json.dumps(full))
            if kind == 'npc':
                self.assertIn('one_box_per_hit', json.dumps(compact))
                self.assertIn('PRIVATE ASPECT GUIDANCE', json.dumps(full))
            self.assertLess(len(json.dumps(compact)), 6500)
        for kwargs in ({'audience': []}, {'detail': {}}, {'audience': 'players'}):
            with self.assertRaises(ValueError):
                g.project(d, **kwargs)

    def test_presentation_reroll_preserves_causal_core_locks_and_source(self):
        g = self.engine()
        d = g.generate(dict(kind='npc', name='Canon Name', location_name='Canon Place', seed=9, mode='scene', context='exact note'))
        d['canon_notes'] = ['Already established: the party owns a gate key.']
        d['npc']['gm']['objective'] = 'Authored custom objective remains untouched.'
        r = g.reroll(d, seed=12)
        self.assertEqual(r, g.reroll(d, seed=12))
        self.assertNotEqual(r['npc']['public']['voice'], d['npc']['public']['voice'])
        self.assertNotEqual(r['npc']['public']['appearance'], d['npc']['public']['appearance'])
        self.assertEqual(d['npc']['name'], 'Canon Name')
        for key in ('request', 'canon_notes', 'situation'):
            self.assertEqual(r[key], d[key])
        for key in ('id', 'name', 'location_ref', 'gm', 'mechanics'):
            self.assertEqual(r['npc'][key], d['npc'][key])
        for key in ('id', 'name', 'npc_refs', 'gm', 'scene'):
            self.assertEqual(r['location'][key], d['location'][key])
        for key in ('seed', 'bundle_id', 'content_version', 'generator_version'):
            self.assertEqual(r['provenance'][key], d['provenance'][key])
        self.assertEqual(r['provenance']['presentation_seed'], 12)
        self.assertEqual(g.validate_draft(r), r)
        self.assertEqual(g.reroll(r, seed=13)['provenance']['presentation_revision'], 2)
        self.assertIsInstance(g.reroll(r)['provenance']['presentation_seed'], int)
        for kwargs in ({'group': 'mechanics'}, {'group': []}, {'seed': True}):
            with self.assertRaises(ValueError):
                g.reroll(d, **kwargs)

    def test_cli_generate_project_reroll_and_render_end_to_end(self):
        root = Path(__file__).resolve().parent.parent
        def cli(*args):
            return subprocess.run([sys.executable, '-m', 'cardmaker', *args], cwd=root, capture_output=True)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source.json'
            created = cli('generate', 'npc', '--ruleset', 'condensed', '--tier', 'main', '--genre', 'noir', '--seed', '42', '--name', 'CLI Name', '--location-name', 'CLI Place', '--context', 'canon note', '--mode', 'scene', '--format', 'draft', '--output', str(source))
            self.assertEqual(created.returncode, 0, created.stderr)
            draft = json.loads(source.read_text())
            self.assertEqual(draft['provenance']['seed'], 42)
            for fmt in ('json', 'text', 'svg', 'png'):
                run = cli('project', str(source), '--format', fmt, '--detail', 'full')
                self.assertEqual(run.returncode, 0, run.stderr)
                if fmt == 'json':
                    self.assertEqual(json.loads(run.stdout)['title'], 'CLI Name')
                elif fmt == 'text':
                    self.assertIn(b'Academics', run.stdout)
                    self.assertIn(b'multiple_boxes_per_hit', run.stdout)
                elif fmt == 'svg':
                    import xml.etree.ElementTree as ET
                    self.assertEqual(ET.fromstring(run.stdout).tag, '{http://www.w3.org/2000/svg}svg')
                else:
                    self.assertTrue(run.stdout.startswith(b'\x89PNG\r\n\x1a\n'))
            direct = cli('generate', 'location', '--seed', '42', '--format', 'text')
            self.assertEqual(direct.returncode, 0, direct.stderr)
            self.assertIn(b'Statless reference place', direct.stdout)
            self.assertEqual(json.loads(cli('generate', 'npc', '--seed', 'abc').stdout)['version'], 1)
            rerolled = cli('reroll', str(source), '--seed', '15', '--group', 'presentation', '--format', 'draft')
            self.assertEqual(rerolled.returncode, 0, rerolled.stderr)
            self.assertEqual(json.loads(rerolled.stdout)['provenance']['presentation_seed'], 15)
            public = cli('project', str(source), '--audience', 'public')
            self.assertNotIn(b'canon note', public.stdout)
            for args in [('generate', 'npc', '--name', ''), ('generate', 'location', '--mode', 'fractal'),
                         ('project', str(source), '--audience', 'public', '--format', 'draft'),
                         ('reroll', str(source), '--group', 'mechanics')]:
                run = cli(*args)
                self.assertEqual(run.returncode, 2, (args, run.stderr))
                self.assertNotIn(b'Traceback', run.stderr)

    def test_all_aspect_examples_are_situation_specific_and_contacts_stunt_uses_people(self):
        g = self.engine()
        found_contacts = False
        for genre in ('fantasy', 'noir', 'scifi'):
            for seed in range(30):
                d = g.generate(dict(kind='npc', genre=genre, tier='main', seed=seed))
                for aspect in d['npc']['mechanics']['aspects']:
                    self.assertNotIn('Draw on this established connection', aspect['help'])
                    self.assertNotIn('An obligation attached to this truth', aspect['complication'])
                stunt = d['npc']['mechanics']['stunts'][0]
                if stunt['competency'] == 'Contacts':
                    found_contacts = True
                    self.assertIn('consulting witnesses', stunt['circumstance'])
                    self.assertNotIn('personally inspecting', stunt['circumstance'])
        self.assertTrue(found_contacts)


if __name__ == '__main__':
    unittest.main()

"""Live HTTP integration and executable UI state tests (stdlib + Node)."""
import http.client
import json
from pathlib import Path
import shutil
import subprocess
import threading
import unittest
from unittest.mock import patch


class GeneratorHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from cardmaker.server import make_server
        cls.server = make_server('127.0.0.1', 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, route, payload, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        connection.request('POST', '/api/' + route, json.dumps(payload), headers or {'Content-Type': 'application/json'})
        response = connection.getresponse()
        result = response.status, response.read()
        connection.close()
        return result

    def node_roundtrip(self, raw):
        """Use real JS numbers on raw HTTP JSON, as response.json/import do."""
        if not shutil.which('node'):
            self.skipTest('Node is required for JSON number precision regressions')
        result = subprocess.run(
            ['node', '-e', "process.stdout.write(JSON.stringify(JSON.parse(require('node:fs').readFileSync(0,'utf8'))))"],
            input=raw, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_default_seed_survives_node_json_and_http_project_reroll(self):
        # Maximal entropy forces the old 63-bit default to lose precision in JS.
        # Honor the requested width so the same fixture exercises the safe fix.
        with patch('cardmaker.generator.secrets.randbits', side_effect=lambda bits: (1 << bits) - 1):
            code, raw = self.post('generate', {'request': {'kind': 'npc', 'mode': 'scene'}})
            self.assertEqual(code, 200, raw)
            original = json.loads(raw)
            generated = self.node_roundtrip(raw)
            self.assertEqual(generated['draft'], original['draft'], 'JSON changed the generated seed')
            seed = generated['draft']['provenance']['seed']
            self.assertIs(type(seed), int)
            self.assertLessEqual(seed, 2 ** 53 - 1)
            code, body = self.post('project', {'draft': generated['draft']})
            self.assertEqual(code, 200, body)
            self.assertEqual(self.node_roundtrip(body)['card'], generated['card'])
            replay_request = {k: v for k, v in generated['draft']['request'].items() if v is not None}
            code, body = self.post('generate', {'request': replay_request})
            self.assertEqual(code, 200, body)
            self.assertEqual(self.node_roundtrip(body), generated)
            code, body = self.post('reroll', {'draft': generated['draft'], 'seed': 42})
            self.assertEqual(code, 200, body)
            rerolled = self.node_roundtrip(body)['draft']
            self.assertEqual(rerolled['npc']['id'], generated['draft']['npc']['id'])
            self.assertEqual(self.post('project', {'draft': rerolled})[0], 200)

    def test_random_presentation_seed_survives_node_json_and_http_replay(self):
        code, body = self.post('generate', {'request': {'kind': 'npc', 'seed': 42}})
        self.assertEqual(code, 200, body)
        source = self.node_roundtrip(body)['draft']
        with patch('cardmaker.generator.secrets.randbits', side_effect=lambda bits: (1 << bits) - 1):
            code, raw = self.post('reroll', {'draft': source})
            self.assertEqual(code, 200, raw)
            original = json.loads(raw)
            rerolled = self.node_roundtrip(raw)
            self.assertEqual(rerolled['draft'], original['draft'], 'JSON changed the presentation seed')
            seed = rerolled['draft']['provenance']['presentation_seed']
            self.assertIs(type(seed), int)
            self.assertLessEqual(seed, 2 ** 53 - 1)
            code, body = self.post('reroll', {'draft': source, 'seed': seed})
            self.assertEqual(code, 200, body)
            self.assertEqual(self.node_roundtrip(body), rerolled)
            code, body = self.post('project', {'draft': rerolled['draft']})
            self.assertEqual(code, 200, body)
            self.assertEqual(self.node_roundtrip(body)['card'], rerolled['card'])
            self.assertEqual(self.post('reroll', {'draft': rerolled['draft']})[0], 200)

    def test_unsafe_numeric_seed_generation_reroll_and_import_are_clear_errors(self):
        code, body = self.post('generate', {'request': {'kind': 'npc', 'seed': 42}})
        self.assertEqual(code, 200, body)
        source = json.loads(body)['draft']
        for seed in (2 ** 53, -(2 ** 53), 2 ** 63 - 1):
            cases = [('generate', {'request': {'kind': 'npc', 'seed': seed}}),
                     ('reroll', {'draft': source, 'seed': seed})]
            for parent, key in (('request', 'seed'), ('provenance', 'seed'), ('provenance', 'presentation_seed')):
                bad = json.loads(json.dumps(source))
                bad[parent][key] = seed
                cases.extend((route, {'draft': bad}) for route in ('project', 'reroll'))
            for route, payload in cases:
                # Cover raw numeric files/API calls and browser-rounded imports.
                for value in (payload, self.node_roundtrip(json.dumps(payload).encode())):
                    with self.subTest(seed=seed, route=route, payload=value):
                        code, error = self.post(route, value)
                        self.assertEqual(code, 400, error)
                        self.assertRegex(error.decode(), 'safe integer.*string')
                        self.assertNotIn(b'provenance', error.lower().split(b':', 1)[-1])

    def test_safe_boundaries_and_large_decimal_strings_replay_through_node_http(self):
        safe = 2 ** 53 - 1
        for seed in (-safe, 0, safe, str(2 ** 63 - 1), '0' * 100 + str(2 ** 63 - 1)):
            with self.subTest(seed=seed):
                request = {'kind': 'location', 'mode': 'scene', 'seed': seed}
                code, raw = self.post('generate', {'request': request})
                self.assertEqual(code, 200, raw)
                generated = self.node_roundtrip(raw)
                self.assertEqual(generated, json.loads(raw))
                draft = generated['draft']
                for actual in (draft['request']['seed'], draft['provenance']['seed'], draft['provenance']['presentation_seed']):
                    self.assertIs(type(actual), type(seed))
                    self.assertEqual(actual, seed)
                code, body = self.post('project', {'draft': draft})
                self.assertEqual(code, 200, body)
                self.assertEqual(self.node_roundtrip(body)['card'], generated['card'])
                code, body = self.post('generate', {'request': request})
                self.assertEqual(code, 200, body)
                self.assertEqual(self.node_roundtrip(body), generated)
                code, raw = self.post('reroll', {'draft': draft, 'seed': seed})
                self.assertEqual(code, 200, raw)
                rerolled = self.node_roundtrip(raw)
                self.assertEqual(rerolled, json.loads(raw))
                self.assertEqual(rerolled['draft']['provenance']['presentation_seed'], seed)
                self.assertEqual(rerolled['draft']['npc']['id'], draft['npc']['id'])
                code, body = self.post('reroll', {'draft': draft, 'seed': seed})
                self.assertEqual(code, 200, body)
                self.assertEqual(self.node_roundtrip(body), rerolled)
                self.assertEqual(self.post('project', {'draft': rerolled['draft']})[0], 200)

    def test_generation_rejects_unbounded_unknown_or_wrong_type_options(self):
        for request in ([], {'unknown': True}, {'kind': 'dragon'}, {'ruleset': []},
                        {'seed': True}, {'seed': {}}, {'seed': 'x' * 257},
                        {'seed': 2 ** 64}, {'name': 42}, {'name': 'n' * 201},
                        {'context': 'x' * 4001}, {'mode': 'fractal'}):
            with self.subTest(request=repr(request)[:80]):
                code, body = self.post('generate', {'request': request})
                self.assertEqual(code, 400, body)
                self.assertTrue(body)


    def test_semantic_routes_reject_invalid_envelopes_before_engine(self):
        cases = [('generate', {'request': {}, 'audience': []}),
                 ('generate', {'request': {}, 'detail': 'giant'}),
                 ('generate', {'request': {}, 'path': '/etc/passwd'}),
                 ('project', {'draft': []}), ('project', {'draft': {}, 'audience': 'players'}),
                 ('project', {'draft': {}, 'theme': 'dark'}),
                 ('reroll', {'draft': {}, 'group': 'situation'}),
                 ('reroll', {'draft': {}, 'seed': False}),
                 ('reroll', {'draft': {}, 'seed': ''}),
                 ('reroll', {'draft': {}, 'unknown': 1})]
        for route, payload in cases:
            with self.subTest(route=route, payload=payload):
                self.assertEqual(self.post(route, payload)[0], 400)


    def test_deep_json_is_a_controlled_client_error(self):
        # Python 3.13 can decode depth 1200: force the decoder's own limit,
        # while staying below the independent 65536-byte HTTP request bound.
        raw = '{"request":' + '[' * 20000 + '0' + ']' * 20000 + '}'
        self.assertLess(len(raw.encode()), 65536)
        for route in ('generate', 'project', 'reroll', 'json', 'svg', 'text', 'png'):
            with self.subTest(route=route):
                connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
                try:
                    connection.request('POST', '/api/' + route, raw, {'Content-Type': 'application/json'})
                    response = connection.getresponse()
                    body = response.read()
                    self.assertEqual(response.status, 400, body)
                    self.assertTrue(body)
                    self.assertLess(len(body), 200)
                    self.assertNotIn(b'Traceback', body)
                finally:
                    connection.close()
                # A rejected request must leave the live server usable.
                code, body = self.post('generate', {'request': {'kind': 'npc', 'seed': 'after-deep-json'}})
                self.assertEqual(code, 200, body)
                self.assertIn('card', json.loads(body))


    def test_export_bad_types_do_not_crash_http_handler(self):
        card = {'version': 1, 'kind': [], 'title': 'Test', 'tags': [], 'fields': []}
        self.assertEqual(self.post('json', {'card': card})[0], 400)


    def test_real_engine_generate_public_projection_reroll_and_exports(self):
        # No engine substitute: this exercises the concurrent engine through HTTP.
        request = {'kind': 'npc', 'ruleset': 'core', 'seed': 'http-ui-test',
                   'name': 'HTTP NPC Ω', 'context': 'GM_CONTEXT_SENTINEL_8341'}
        code, body = self.post('generate', {'request': request, 'audience': 'public', 'detail': 'full'})
        self.assertEqual(code, 200, body)
        generated = json.loads(body)
        self.assertEqual(set(generated), {'draft', 'card'})
        source = generated['draft']
        # The response is a local GM workspace, NOT itself a public export.
        secret = source['npc']['gm']['secret']['fact']
        self.assertEqual(source['npc']['name'], 'HTTP NPC Ω')
        self.assertNotIn(secret, json.dumps(generated['card'], ensure_ascii=False))
        self.assertNotIn(request['context'], json.dumps(generated['card']))
        self.assertLessEqual(set(generated['card']), {'version', 'kind', 'title', 'subtitle', 'tags', 'fields'})
        code, body = self.post('project', {'draft': source, 'audience': 'gm', 'detail': 'full'})
        self.assertEqual(code, 200, body)
        self.assertIn(secret, json.dumps(json.loads(body)['card'], ensure_ascii=False))
        code, body = self.post('project', {'draft': source, 'audience': 'public', 'detail': 'full'})
        self.assertEqual(code, 200, body)
        public = json.loads(body)
        self.assertEqual(set(public), {'card'})
        self.assertEqual(public['card'], generated['card'])
        for format in ('json', 'svg', 'png', 'text'):
            code, exported = self.post(format, {'card': public['card'], 'theme': 'dark'})
            self.assertEqual(code, 200, exported[:200])
            self.assertTrue(exported)
            self.assertNotIn(secret.encode(), exported)
            self.assertNotIn(request['context'].encode(), exported)
            if format == 'json':
                self.assertEqual(json.loads(exported), public['card'])
        code, body = self.post('reroll', {'draft': source, 'group': 'presentation', 'seed': 'new-appearance', 'audience': 'public'})
        self.assertEqual(code, 200, body)
        rerolled = json.loads(body)
        self.assertEqual(rerolled['draft']['npc']['name'], source['npc']['name'])
        self.assertEqual(rerolled['draft']['location']['name'], source['location']['name'])
        self.assertEqual(rerolled['draft']['situation'], source['situation'])
        self.assertEqual(rerolled['draft']['npc']['gm'], source['npc']['gm'])
        self.assertNotIn(secret, json.dumps(rerolled['card'], ensure_ascii=False))
        self.assertEqual(self.post('project', {'draft': {'version': 99}})[0], 400)


class GeneratorBrowserLogicTests(unittest.TestCase):
    """Run actual app.js against a tiny DOM/transport double, not a fake engine."""
    def run_ui(self, assertions):
        harness = r'''
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
class Element {
  constructor(tag='div') { this.tagName=tag.toUpperCase(); this.children=[]; this.value=''; this.dataset={}; this.disabled=false; this.listeners={}; }
  append(...items) { for(const item of items) if(typeof item!=='string') {item.parent=this;this.children.push(item);} }
  replaceChildren(...items) { this.children=[]; this.append(...items); }
  querySelector(tag) { return this.children.find(c=>c.tagName===tag.toUpperCase()) || this.children.flatMap(c=>c.querySelectorAll(tag))[0]; }
  querySelectorAll(tag) { return this.children.flatMap(c=>[...(c.tagName===tag.toUpperCase()?[c]:[]),...c.querySelectorAll(tag)]); }
  addEventListener(name, fn) { this.listeners[name]=fn; }
  remove() {this.parent.children=this.parent.children.filter(c=>c!==this);}
  click() {if(this.tagName==='A') downloads.push({download:this.download,href:this.href});return this.onclick?.();}
  focus() {} select() {}
}
const ids={};
const html=fs.readFileSync('cardmaker/ui.html','utf8');
for(const match of html.matchAll(/id="([^"]+)"/g)) ids[match[1]]=new Element();
const defaults={kind:'npc',theme:'dark',title:'Untitled card',genKind:'npc',ruleset:'core',tier:'supporting',genre:'fantasy',mode:'place',audience:'gm',detail:'compact'};
for(const [key,value] of Object.entries(defaults)) if(ids[key]) ids[key].value=value;
const buttons=['svg','png','text','json'].map(format=>{const e=new Element('button');e.dataset.export=format;return e;});
const calls=[],downloads=[],blobs=[];
const sampleCard={version:1,kind:'npc',title:'TEST NPC',subtitle:'Proposed',tags:[],fields:[{label:'Visible',value:'Test description'}]};
const sampleDraft={draft_version:1,generator_version:'TEST',content_version:'TEST',seed:'test-seed',request:{kind:'npc'},npc:{name:'TEST NPC'},location:{name:'TEST PLACE'}};
let confirmResult=true, confirmations=0;
const context={console,Blob,setTimeout:()=>{},URL:{createObjectURL:blob=>{blobs.push(blob);return 'blob:test';},revokeObjectURL:()=>{}},navigator:{clipboard:{writeText:async()=>{}}},
 confirm:()=>{confirmations++;return confirmResult;},
 document:{getElementById:id=>ids[id],createElement:tag=>new Element(tag),querySelectorAll:()=>buttons},
 fetch:async(path,options)=>{
   const payload=JSON.parse(options.body); calls.push({path,payload});
   const result=path==='/api/project'?{card:sampleCard}:path==='/api/generate'||path==='/api/reroll'?{draft:sampleDraft,card:sampleCard}:payload.card;
   return {ok:true,json:async()=>structuredClone(result),text:async()=>JSON.stringify(result),blob:async()=>new Blob(['test'])};
 }};
vm.createContext(context);vm.runInContext(fs.readFileSync('cardmaker/app.js','utf8'),context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{await flush();
'''
        result = subprocess.run(['node', '-'], input=harness + assertions + '\n})().catch(e=>{console.error(e);process.exitCode=1;});', text=True, capture_output=True, cwd=Path(__file__).parent.parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generate_options_load_server_projected_card(self):
        self.run_ui(r'''
assert.ok(ids.generate, 'Generation controls must exist');
ids.genKind.value='npc';ids.ruleset.value='accelerated';ids.tier.value='main';
ids.genre.value='scifi';ids.mode.value='scene';ids.seed.value='reproduce-me';
ids.genName.value='Test Person';ids.locationName.value='Test Place';ids.context.value='Unparsed test note';
await ids.generate.onclick();
const call=calls.find(c=>c.path==='/api/generate');assert.ok(call);
assert.deepEqual(call.payload,{request:{kind:'npc',ruleset:'accelerated',tier:'main',genre:'scifi',mode:'scene',seed:'reproduce-me',name:'Test Person',location_name:'Test Place',context:'Unparsed test note'},audience:'gm',detail:'compact'});
assert.equal(ids.title.value,'TEST NPC');
assert.equal(ids.image.src,'blob:test');
''')


    def test_draft_import_projection_reroll_and_separate_gm_source(self):
        self.run_ui(r'''
assert.ok(ids.source, 'A separate GM-only source download is required');
ids.json.value=JSON.stringify(sampleDraft);await ids.import.onclick();
assert.ok(calls.some(c=>c.path==='/api/project'&&c.payload.draft.seed==='test-seed'));
assert.match(ids.sourceStatus.textContent,/test-seed/);
assert.match(ids.sourceStatus.textContent,/TEST/);
assert.match(ids.sourceStatus.textContent,/not canon/i);
await ids.source.onclick();
assert.equal(downloads.at(-1).download,'generator-source-gm-only.json');
assert.deepEqual(JSON.parse(await blobs.at(-1).text()),sampleDraft);
ids.audience.value='public';await ids.audience.onchange();
assert.equal(calls.filter(c=>c.path==='/api/project').at(-1).payload.audience,'public');
assert.equal(ids.source.disabled,true);
const downloadCount=downloads.length;await ids.source.onclick();assert.equal(downloads.length,downloadCount);
ids.detail.value='full';await ids.detail.onchange();
assert.equal(calls.filter(c=>c.path==='/api/project').at(-1).payload.detail,'full');
ids.rerollSeed.value='new-look';await ids.reroll.onclick();
const rerollCall=calls.find(c=>c.path==='/api/reroll');
assert.equal(rerollCall.payload.group,'presentation');assert.equal(rerollCall.payload.seed,'new-look');
await buttons.find(b=>b.dataset.export==='json').onclick();
const exported=calls.filter(c=>c.path==='/api/json').at(-1).payload;
assert.deepEqual(Object.keys(exported).sort(),['card','theme']);
assert.equal(exported.card.title,'TEST NPC');assert.equal(exported.card.draft,undefined);
''')


    def test_form_edits_require_confirmation_before_projection_or_reroll(self):
        self.run_ui(r'''
await ids.generate.onclick();
ids.title.value='MY UNSAVED TITLE';ids.title.oninput();
assert.match(ids.sourceStatus.textContent,/not synced/i);
confirmResult=false;
const count=calls.length;ids.audience.value='public';await ids.audience.onchange();
assert.equal(confirmations,1);assert.equal(calls.length,count);
assert.equal(ids.audience.value,'gm');assert.equal(ids.title.value,'MY UNSAVED TITLE');
await ids.reroll.onclick();assert.equal(calls.length,count);assert.equal(confirmations,2);
await buttons.find(b=>b.dataset.export==='json').onclick();
assert.equal(calls.at(-1).payload.card.title,'MY UNSAVED TITLE');
await ids.source.onclick();assert.equal(JSON.parse(await blobs.at(-1).text()).npc.name,'TEST NPC');
confirmResult=true;ids.audience.value='public';await ids.audience.onchange();
assert.equal(ids.title.value,'TEST NPC');assert.equal(ids.source.disabled,true);
ids.fields.children[0].querySelector('textarea').value='MY EDIT';
ids.fields.children[0].querySelector('textarea').oninput();
confirmResult=false;await ids.generate.onclick();assert.equal(ids.fields.children[0].querySelector('textarea').value,'MY EDIT');
''')


    def test_failed_card_transitions_preserve_card_source_view_edits_and_previews(self):
        for operation in ('project-gm', 'project-public', 'project-detail', 'generate',
                          'import-draft', 'import-card', 'import-file', 'reroll', 'preview'):
            for failure in ('semantic', 'json', 'svg', 'text', 'svg-body', 'text-body'):
                if (operation == 'preview' and failure in ('json', 'semantic') or
                        operation == 'import-card' and failure == 'semantic'):
                    continue
                with self.subTest(operation=operation, failure=failure):
                    self.run_ui('const operation=' + json.dumps(operation) + ';const failure=' + json.dumps(failure) + ';' + r'''
const secret='HIDDEN-FACT-123';
const oldDraft={...sampleDraft,seed:'old-source',gm:{fact:secret}};
const nextDraft={...sampleDraft,seed:'next-source',gm:{fact:secret}};
let generated=0, failAt=null, release;
const revoked=[], images=new Map();let serial=0;
context.URL.createObjectURL=blob=>{const url='blob:'+ ++serial;images.set(url,blob);blobs.push(blob);return url;};
context.URL.revokeObjectURL=url=>revoked.push(url);
const projected=(source,audience)=>({...sampleCard,title:source.seed,fields:[{label:'Fact',value:audience==='gm'?secret:'Visible public fact'}]});
context.fetch=async(path,options)=>{
 const payload=JSON.parse(options.body);calls.push({path,payload});
 const reject=async()=>{await new Promise(resolve=>release=resolve);throw Error('Injected '+failure+' preview failure');};
 if(path===failAt&&!failure.endsWith('-body')) await reject();
 let result=payload.card;
 if(path==='/api/generate') {const draft=generated++?nextDraft:oldDraft;result={draft,card:projected(draft,payload.audience)};}
 if(path==='/api/project') result={card:projected(payload.draft,payload.audience)};
 if(path==='/api/reroll') result={draft:nextDraft,card:projected(nextDraft,payload.audience)};
 return {ok:true,json:async()=>structuredClone(result),
  text:async()=>{if(path===failAt&&failure==='text-body') await reject();return JSON.stringify(result);},
  blob:async()=>{if(path===failAt&&failure==='svg-body') await reject();return new Blob([JSON.stringify(result)]);}};
};
const state=()=>JSON.parse(vm.runInContext('JSON.stringify({card:card(),draft,edited,appliedView,view:viewOptions()})',context));
const snapshot=()=>({...state(),image:ids.image.src,text:ids.text.value,sourceStatus:ids.sourceStatus.textContent});
const exportCard=async()=>{await buttons.find(b=>b.dataset.export==='json').onclick();return calls.at(-1).payload;};
await ids.generate.onclick();
if(operation!=='project-public') {ids.audience.value='public';await ids.audience.onchange();}
// Preserve real authoring edits too, not only the projected card and selectors.
ids.title.value+=' edited';ids.title.oninput();
await ids.preview.onclick();
const before=snapshot();
assert.equal(before.edited,true);
if(before.view.audience==='public') assert.ok(!JSON.stringify(before.card).includes(secret));
const act=async()=>{
 if(operation==='project-gm') {ids.audience.value='gm';return ids.audience.onchange();}
 if(operation==='project-public') {ids.audience.value='public';return ids.audience.onchange();}
 if(operation==='project-detail') {ids.detail.value='full';return ids.detail.onchange();}
 if(operation==='generate') return ids.generate.onclick();
 if(operation==='reroll') return ids.reroll.onclick();
 if(operation==='preview') return ids.preview.onclick();
 if(operation==='import-file') {ids.file.files=[{size:100,text:async()=>JSON.stringify(nextDraft)}];return ids.file.onchange();}
 ids.json.value=JSON.stringify(operation==='import-draft'?nextDraft:{...sampleCard,title:'Imported authored card'});
 return ids.import.onclick();
};
if(operation!=='preview') {
 confirmResult=false;const count=calls.length;await act();
 assert.equal(calls.length,count,'cancelled replacement must not request any new card');
 assert.deepEqual(snapshot(),before,'cancelled replacement must preserve source, edits and previews');
 confirmResult=true;
}
const semanticRoute=operation==='generate'?'generate':operation==='reroll'?'reroll':'project';
failAt='/api/'+(failure==='semantic'?semanticRoute:failure.replace('-body',''));
const pending=act();await flush();assert.equal(typeof release,'function');
const during=snapshot();
assert.equal(ids.editorControls.disabled,true);
release();await pending;failAt=null;
assert.match(ids.status.textContent,/Injected/);
assert.deepEqual(snapshot(),before,'failed install must preserve the entire card/source/view/edit/preview state');
assert.deepEqual(during,before,'pending projection must not relabel old GM previews as public or mutate the card');
assert.ok(!revoked.includes(before.image),'failed preparation must retain the old live image URL');
const exported=await exportCard();assert.deepEqual(exported.card,before.card);
assert.deepEqual(Object.keys(exported).sort(),['card','theme']);
if(before.view.audience==='public') {
 assert.ok(!JSON.stringify(exported).includes(secret));
 assert.ok(!(await images.get(ids.image.src).text()).includes(secret));
 assert.ok(!ids.text.value.includes(secret));
 const n=downloads.length;await ids.source.onclick();assert.equal(downloads.length,n);
} else {
 await ids.source.onclick();assert.deepEqual(JSON.parse(await blobs.at(-1).text()),oldDraft);
}
// A retry must commit the new association as well as both previews.
await act();
const after=state();
if(operation==='import-card') {assert.equal(after.draft,null);assert.equal(ids.reroll.disabled,true);}
else if(['generate','reroll','import-draft','import-file'].includes(operation)) assert.deepEqual(after.draft,nextDraft);
else assert.deepEqual(after.draft,oldDraft);
assert.deepEqual(after.view,after.appliedView);
assert.equal(after.edited,operation==='preview');
assert.equal(ids.text.value,JSON.stringify(after.card));
assert.equal(await images.get(ids.image.src).text(),JSON.stringify(after.card));
if(after.view.audience==='public') assert.ok(!JSON.stringify(await exportCard()).includes(secret));
''')

    def test_slow_generation_locks_authoring_and_prevents_overlapping_actions(self):
        self.run_ui(r'''
const baseFetch=context.fetch;let release;
context.fetch=async(path,options)=>{
 if(path==='/api/generate') await new Promise(resolve=>release=resolve);
 return baseFetch(path,options);
};
const pending=ids.generate.onclick();await flush();
assert.equal(ids.editorControls.disabled,true);
assert.equal(ids.generationControls.disabled,true);
assert.equal(ids.audience.disabled,true);
await ids.reroll.onclick();
assert.equal(calls.some(c=>c.path==='/api/reroll'),false);
release();await pending;
assert.equal(ids.editorControls.disabled,false);assert.equal(ids.audience.disabled,false);
''')

    def test_generic_import_stays_unfiltered_and_warns(self):
        self.run_ui(r'''
ids.json.value=JSON.stringify(sampleCard);await ids.import.onclick();
ids.audience.value='public';await ids.audience.onchange();
assert.equal(calls.some(c=>c.path==='/api/project'),false);
assert.match(ids.sourceStatus.textContent,/cannot safely infer GM/i);
assert.match(ids.sourceStatus.textContent,/unfiltered/i);
assert.equal(ids.title.value,'TEST NPC');assert.equal(ids.reroll.disabled,true);
ids.add.onclick();ids.fields.children.at(-1).querySelector('input').value='Custom';
ids.fields.children.at(-1).querySelector('textarea').value='User value';
await ids.preview.onclick();
assert.equal(calls.at(-1).payload.card.fields.at(-1).value,'User value');
''')


    def test_location_uses_entity_name_without_conflicting_linked_place_option(self):
        self.run_ui(r'''
ids.genKind.value='location';ids.genName.value='Chosen Station';ids.locationName.value='Other Place';
ids.genKind.onchange();assert.equal(ids.locationName.disabled,true);
await ids.generate.onclick();
const request=calls.find(c=>c.path==='/api/generate').payload.request;
assert.equal(request.name,'Chosen Station');assert.equal(request.location_name,undefined);
''')


    def test_real_draft_provenance_metadata_is_visible(self):
        self.run_ui(r'''
sampleDraft.provenance={seed:9182,generator_version:'1.2.3',content_version:'pack-4'};
delete sampleDraft.seed;delete sampleDraft.generator_version;delete sampleDraft.content_version;
await ids.generate.onclick();
assert.match(ids.sourceStatus.textContent,/9182/);
assert.match(ids.sourceStatus.textContent,/1\.2\.3/);
assert.match(ids.sourceStatus.textContent,/pack-4/);
''')


if __name__ == '__main__':
    unittest.main()

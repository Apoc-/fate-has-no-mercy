# Cardmaker

A small local RPG note-card editor and Python CLI. Gene (or a person) authors structured JSON; this app validates, edits, and renders it. No external AI API, account, framework, or Tk display needed. The Python standard library handles SVG, text, and the HTTP UI. PNG additionally requires Pillow.

## Run

Use Python 3.10+ **from the repository root**, not inside `cardmaker/`:

```sh
python -m cardmaker --help
python -m cardmaker ui --host 127.0.0.1 --port 8765
```

Open <http://127.0.0.1:8765> in your browser. Ctrl-C stops the server. `--port 0` chooses an available port and prints its URL. This is a loopback-only personal tool, not a public production server.

For optional PNG export (Pillow 13.0.0 was available during verification):

```sh
python -m venv cardmaker/.venv
cardmaker/.venv/bin/python -m pip install -r cardmaker/requirements.txt
cardmaker/.venv/bin/python -m cardmaker ui
```

### CLI

```sh
python -m cardmaker render cardmaker/examples/npc.json --format text
python -m cardmaker render cardmaker/examples/npc.json --format svg --output cardmaker/examples/output/npc.svg
python -m cardmaker render cardmaker/examples/npc.json --format png --output cardmaker/examples/output/npc.png
python -m cardmaker render cardmaker/examples/location.json --format svg --theme parchment --output cardmaker/examples/output/location.svg
python -m cardmaker render cardmaker/examples/character.json --format text --output cardmaker/examples/output/character.txt
python -m cardmaker render cardmaker/examples/npc.json --format svg --theme cardmaker/themes/parchment.json --output cardmaker/examples/output/custom-theme.svg
```

`--format` defaults to `svg`. Without `--output`, all formats write to stdout, including binary PNG; **use an output path for images**. Text stdout is UTF-8 and copy/paste friendly. Errors go to stderr with exit code 2; successful renders exit 0. Output parent directories are created by the CLI only.

## Local generation (semantic draft v1)

The generator is an **offline, original situation-pack engine**, not an API client or an adjective randomizer. Nine authored bundles (three each for fantasy, noir and science fiction) connect a resource dispute, NPC agenda, obstacle, offer, boundary, relationship, secret and three discovery options to a specific place with interactive features, pressure, warning, counterplay and open choices. These are proposals, not campaign canon or balanced encounters. A seed chooses among a deliberately small library; it does not imply unlimited fictional diversity.

### Commands

Run from the repository root:

```sh
python -m cardmaker generate npc --ruleset core --tier supporting --genre fantasy --seed 42 --name "Aster" --location-name "Old Sluice" --format text
python -m cardmaker generate location --genre scifi --mode scene --seed 42 --format svg --output cardmaker/examples/output/generated-scene.svg
# Save the full GM semantic source separately from the generic render card:
python -m cardmaker generate npc --ruleset condensed --tier main --genre noir --seed 42 --context "Existing canon: the party has a key." --format draft --output cardmaker/examples/output/generated-source.json
python -m cardmaker project cardmaker/examples/output/generated-source.json --detail full --format json --output cardmaker/examples/output/generated-gm.json
python -m cardmaker project cardmaker/examples/output/generated-source.json --audience public --format png --output cardmaker/examples/output/generated-public.png
python -m cardmaker reroll cardmaker/examples/output/generated-source.json --group presentation --seed 9 --format draft --output cardmaker/examples/output/rerolled-source.json
```

Generation/project/reroll default to a **generic v1 JSON card**, GM audience, compact detail. Formats: `json`, `draft`, `text`, `svg`, `png`; themes and output behavior match `render`. `draft` is GM-only because it contains the secret and full source; `--audience public --format draft` errors. Public card projections contain only an explicit visible-field allowlist and **no embedded source or unknown metadata**. GM full includes discovery channels, detailed aspect guidance, assumptions, user context and canon notes. Compact omits that guidance rather than clipping text; full cards may be tall. PNG still needs existing Pillow and respects the renderer's pixel safety cap.

### Locked Python API (for the browser integration)

```python
from cardmaker import generator
source = generator.generate({"kind": "npc", "seed": 42})
generator.validate_draft(source)  # returns the same valid draft, otherwise ValueError
card = generator.project(source, audience="gm", detail="compact")
new_source = generator.reroll(source, group="presentation", seed=9)
```

`generate(request: dict) -> draft`, `project(draft, audience='gm', detail='compact') -> v1 card`, `reroll(draft, group='presentation', seed=None) -> new draft`, `validate_draft(draft) -> draft` are real functions. Project selects `draft.request.kind`; both linked entities remain in the separate source. Do not pass a generic v1 card to the draft APIs, or reconstruct source from the form's render fields.

Request keys are **only** `kind` (required: `npc|location`), `ruleset` (`neutral|core|condensed|accelerated`, default **core**, an explicit project assumption), `tier` (`mook|supporting|main`, default supporting), `genre` (`fantasy|noir|scifi`, default fantasy), `seed` (optional JSON-safe integer in the inclusive range `-9007199254740991` to `9007199254740991`, not bool, or nonempty string up to 128 characters), `name` (optional requested entity name), `location_name` (optional linked location name), `context` (optional exact unparsed note), `mode` (`place|scene`, default place). No unknown keys are silently ignored. API strings stay strings; CLI decimal seed tokens become integers. Missing seed uses system entropy and records the resulting integer without touching the global PRNG. Names are at most 120 characters; context at most 2,000. Conflicting location-name locks and duplicate NPC/location names error. Name locks and entity references are checked on import.

Automatic generation and presentation rerolls use nonnegative **53-bit** integer seeds so browser JSON round trips are lossless. The same numeric bounds apply to direct Python calls, CLI numeric tokens, HTTP requests, and every seed field in imported drafts, including presentation metadata. For larger seeds, use a string such as `"9223372036854775807"` through the Python/HTTP API or browser seed field; long decimal strings (up to 128 characters) remain exact strings. The CLI still interprets decimal tokens as integers and rejects out-of-range values. Older drafts with unsupported wide numeric seeds fail with string-seed guidance before provenance/ID comparisons. Recover the exact original seed before browser parsing and use it as a string in a **new generation request**; quoting an already rounded number or changing seed fields in an existing draft cannot repair its provenance or IDs.

Draft keys: `version`, full normalized `request`, `provenance` (generator/content versions, original seed/bundle, separate presentation seed/revision), `situation`, `npc`, `location`, `canon_notes`. NPC and location each separate `public` and `gm` data and use stable source-local IDs; these IDs are not a campaign-wide identity registry. `canon_notes` is a GM-only list of preserved user strings. Context is stored byte-for-byte as a Python/JSON string and labeled **unparsed constraint note**: it is **not** NLP-enforced and can contradict generated fiction, so review it. The engine only enforces the explicit enum/name constraints.

Presentation reroll changes delivery/emphasis labels and sensory ordering, not new appearance facts: it preserves the entire causal situation, names, IDs, references, mechanics, GM edits, context, canon notes and known source. It is intentionally conservative, not a fresh NPC or mechanism. Other reroll groups (including mechanics) error. Save the returned draft; the original is not mutated.

### Rules presets and limits

- **Core:** native nameless mooks use linked Average/Fair/Good skill/stress recipes; supporting uses a reduced four-skill column, one scoped stunt, derived physical/mental tracks and a mild consequence; main uses five aspects and a ten-skill 4/3/3/2/2/2/1/1/1/1 pyramid. Tracks hold escalating box capacities; mark one box per hit. Physique/Will determine track length. Main has empty 2/4/6 consequence slots and labels the extreme-consequence last resort separately.
- **Condensed:** UI mook maps to native **minor**, using two relevant skills, two one-point stress boxes and no consequences. Main maps to **major**, with the main skill pyramid and Academics distinct from supernatural Lore. The intermediate supporting tier is explicitly a **reduced-major project convenience**, not an official third tier. Major-style physical/mental tracks have one-point boxes; several may absorb one hit. Physique/Will thresholds differ from Core.
- **Accelerated:** native mooks use descriptive +2 strengths / -2 weaknesses / unlisted 0, a short unified [1,2] track and no consequences. Main important NPCs have the six native approaches at +3,+2,+2,+1,+1,0, unified [1,2,3] stress and empty 2/4/6 consequence slots. Supporting is an explicitly labeled **project convenience** with reduced approaches, [1,2] stress and one mild slot. Approaches do not grant extra stress.
- **Neutral:** no numeric NPC mechanics, Fate aspects, passive difficulty numbers, skills, attributes, HP or fate pool. Scene connections remain descriptive routes.
- **Places** are statless references, even when their connected NPC has mechanics. **Scenes** add three named connected zones, three scoped situation aspects in Fate profiles, a passive obstacle with explicitly illustrative +2 difficulty, zero initial free invokes and open stakes. Counts/difficulty are project examples, not universal Fate mandates. **Fractal/location-as-character is unsupported** and rejected.

No grouped-mook rules, automatic aspect +2s, private NPC fate pools, campaign-level encounter balance, automatic promotion, recovery automation, optional boss modules, custom content-pack import or arbitrary hacked Fate sheet import is implemented. Stunts are narrow create-advantage inspection proposals labeled **table review**; approve their fit before play. Ordinary consequences begin empty, not as invented injuries. `generation_schema.json` documents strict structure; runtime additionally checks name locks, references, source versions, zone graph and exact known mechanics presets. Narrative text edits and canon notes are supported, but the validator cannot prove arbitrary prose logically coherent or safely classify a secret someone manually pastes into a public field. Review visibility when authoring. Unknown versions or unsupported mechanics edits error rather than claiming migration support. Save complete drafts: a seed alone cannot reproduce a later changed generator/content version.

Rules/design grounding (paraphrased procedures; original fiction, no copied random tables): [Core opposition](https://fate-srd.com/fate-core/creating-and-playing-opposition), [Core stress](https://fate-srd.com/fate-core/stress-consequences), [Condensed creation](https://fate-srd.com/fate-condensed/getting-started), [Condensed GM](https://fate-srd.com/fate-condensed/being-game-master), [FAE GM](https://fate-srd.com/fate-accelerated/being-gamemaster), [FAE stress](https://fate-srd.com/fate-accelerated/ouch-damage-stress-and-consequences), [places](https://fate-srd.com/fate-core/faces-places), [scenes](https://fate-srd.com/fate-core/setting-scene), [aspect design](https://fate-srd.com/fate-core/making-good-aspect), [NPC roleplaying template](https://thealexandrian.net/wordpress/37916/roleplaying-games/universal-npc-roleplaying-template), [prep situations](https://thealexandrian.net/wordpress/4147/roleplaying-games/dont-prep-plots), [secrets and clues](https://slyflourish.com/sharing_secrets.html), [location moves](https://slyflourish.com/location_moves.html). Relevant mechanical recipes were cross-checked against the [official redistributable SRDs](https://fate-srd.com/official-licensing-fate); the web presentation is not a redistributable text source.

Generator regression command: `python -m unittest cardmaker.test_generator cardmaker.test_cardmaker -v`. Tests were developed in vertical RED/GREEN slices and exercise actual CLI outputs, not fabricated responses.

## Authoring contract (version 1)

```json
{
  "version": 1,
  "kind": "npc",
  "title": "Example: The bell keeper",
  "subtitle": "Fictional example; not campaign canon",
  "tags": ["example", "fictional"],
  "fields": [
    {"label": "Motive", "value": "Recover a missing ledger."},
    {"label": "Notes", "value": "First line.\nSecond line."}
  ]
}
```

- Required: `version`, `kind`, `title`, `tags`, `fields`. Only `subtitle` is optional.
- Kinds: `npc`, `location`, `character`, `item`, `faction`, `note`.
- Titles and field labels must contain non-whitespace text. Field values, tags, subtitle must be strings; empty values and empty lists are allowed.
- Fields are generic and ordered, not rules-system-specific. All kinds use the same renderer. UI presets add suggested blank fields without overwriting your existing content.
- Unknown keys are accepted and preserved by CLI/backend JSON export, but are not rendered. The form edits only the documented contract; keep your source separately if adding extension keys.
- `schema.json` documents the structural contract. Runtime also rejects XML-incompatible characters and cards over 65,536 UTF-8 bytes. The UI request envelope shares that limit, so leave a little headroom for UI imports.
- JSON is data, not code or HTML. Local deterministic generation is available through the CLI and `/api/generate`; it does not execute embedded prompts or call an AI API. Agent-authored cards can still use this generic contract directly.

The three supplied cards in `examples/` are **authored fictional examples, not campaign canon**: an NPC, location, and character. Their exported SVG/PNG files are in `examples/output/`.

## Browser editor

Choose generation settings and **Generate linked proposal** for an NPC or location, or keep editing/importing generic cards as before. Generated sources hold both linked entities; the selected kind determines the projected card. **GM/public** and **compact/full** select trusted projections. Presentation reroll changes emphasis without changing the causal situation. Changes to audience/detail/rerolls require discard confirmation if the card has independent form edits.

**Save GM source backup** preserves regeneration data and secrets; it is disabled in public view. Import accepts both full source drafts and ordinary v1 cards. Generic cards have no reliable visibility classification and remain unfiltered. The local generation API returns a **GM-workspace envelope** containing the full draft even when its accompanying projected card is public: share only the public card, never the whole response/source. The source backup does not incorporate independent form edits.

For manual editing, choose a kind/theme, enter title/subtitle/tags and arbitrary labeled fields, then **Update preview**. Preview refresh is explicit (changing the theme also refreshes it). Import by pasting JSON or opening a JSON file. Download SVG, PNG, or JSON; **Copy text** uses the clipboard or selects the text area for manual copying if clipboard access is unavailable. Tags use comma separators in the form, so avoid literal commas inside tag names when editing there.

The editor does not autosave. **Download JSON before closing or reloading.** Browser downloads go to your browser's configured download directory. The server does not write cards to disk.

SVG uses escaped native `<text>` lines, explicit dimensions, and no `foreignObject`, scripts, linked resources, or embedded HTML. Text wraps (including long unbroken words and wide Unicode) and card height grows without silently truncating content. Cards are 640 px wide. A monospaced font makes wrapping predictable across importers. SVG text remains editable; target apps may substitute fonts. PNG uses DejaVu Sans Mono when installed, otherwise Pillow's default font. Unicode is preserved, but glyph coverage (especially emoji/CJK) depends on installed fonts; missing glyphs are not an AI/content error. Very tall PNGs are explicitly rejected above 16 million pixels rather than allocating unbounded memory; SVG/text remain available.

## Themes and extension points

Built-in theme token files are `themes/dark.json` and `themes/parchment.json`. CLI `--theme` also accepts a JSON path with these four `#RRGGBB` tokens:

```json
{"background":"#181d27","foreground":"#eef0f5","muted":"#aeb8cc","accent":"#dfb879"}
```

Only built-in themes are selectable through HTTP; request data cannot name files. New kind-specific mechanics should remain labeled fields rather than change version 1's basic contract. Keep future configurable dimensions/fonts explicit and bounded.

## Security boundary

Server binds only `127.0.0.1`/`localhost`, validates Host and Origin, rejects other origins, serves only three explicit UI paths, and has no arbitrary file read/write or directory-listing route. POSTs require JSON and bounded Content-Length. SVG escapes text and theme tokens are validated colors. The UI uses DOM text/value APIs, never inserts authored HTML, and CSP limits scripts/styles/resources to the local app. Keep it local; this is not an authenticated multi-user service. Avoid opening untrusted local apps that can already read your files.

## Tests

With Pillow installed:

```sh
python -m unittest discover -s cardmaker -t . -v
python -m compileall -q cardmaker
node --check cardmaker/app.js
```

Node is used for UI logic/syntax tests only; the Python application itself does not require it. See [research findings and source evidence](research/README.md) for the design rationale, inspected generators, rules boundaries and remaining scope limits.

The suite covers the contract, invalid/oversized content, portable wrapping/escaping/autoheight, wide Unicode, PNG dimensions/resource bounds, CLI stdout/errors, live HTTP exports, traversal rejection, cross-origin/host rejection, and theme-path rejection. Development followed vertical red/green slices. Browser smoke verification additionally exercised form editing, preview decoding, JSON import, and download endpoints. `charsheet/` and repository workflows are unchanged.

# Cards, themed bundles and renderer integration

Use this procedure for graphical Fate material and downloadable packs. The parent SKILL.md owns the standing German-content/English-terminology and Fate Condensed defaults. This reference describes exports and software boundaries, not another set of game defaults.

## 1. Resolve scope and source

1. Read the current checkout's `cardmaker/README.md` for actual commands and contracts. Work from the repository root; discover its path rather than expecting a user's download to share the agent's filesystem.
2. Enumerate the requested definitions/types and give each a stable ID. A follow-up bundle inherits the latest agreed scope. Store all authored data in one UTF-8 source before rendering so PDF, cards and text cannot drift independently.
3. Use the four Condensed templates for character roles, varying Skills and recomputing Stress. If no other PC exists yet, supply a clearly labeled Relationship proposal and leave its partner to player agreement; do not invent an established PC or silently replace the PC Relationship with an NPC bond.
4. Treat a named genre/theme as tone and visual direction. Keep town/building/incidentals at the requested zoom; local relationships are fine, but do not establish a shared conflict, main quest, hidden plot or deadline unless requested. Use an existing film's characters only when explicitly requested. For a Western, a restrained palette, serif poster headings and simple double rules can convey the genre without stereotypes, decorative clutter or mandatory gunfights.
5. Keep all private notes in an explicitly GM-facing pack. Do not imply that ordinary v1 JSON has enforceable public/GM field metadata.

## 2. Produce renderable cards

The v1 card object contains `version: 1`, `kind`, `title`, optional `subtitle`, `tags`, and ordered `fields` objects with string `label`/`value`. Accepted kinds: `npc`, `location`, `character`, `item`, `faction`, `note`. Map other content to an appropriate generic kind instead of inventing enum values. If a reusable template wraps `template` metadata plus `card`, extract and render the nested `card`.

Use `write_file` for source JSON. Through `terminal` from the repo root:

```sh
python -m cardmaker render CARD.json --format text
python -m cardmaker render CARD.json --format svg --output CARD.svg
python -m cardmaker render CARD.json --format png --output CARD.png
python -m cardmaker render CARD.json --format png --theme THEME.json --output THEMED.png
```

Read stdout for plain text; use explicit image output paths rather than binary stdout. The custom theme contract is four `#RRGGBB` values: `background`, `foreground`, `muted`, `accent`. Keep these visual tokens separate from narrative source. The reusable Western palette is `templates/themes/movie-western.json`; choose it for that requested theme, not as a global setting. The CLI palette affects renderer colors; a custom poster layout in HTML/PDF is a distinct design and should not be misrepresented as a new UI theme feature.

Preserve one JSON card per definition, but do not equate full source with verbose printed prose. Enforce the main skill's 40-word/four-field Goon and 65-word/five-field Standard NPC budgets. Combine low-detail entries on compact shared sheets; omit repeated setup, rules, absent mechanics and advice. Only long PC/major-NPC sheets need a Profile/Mechanics card and a Stunts/GM Notes companion. Do not change mechanical values when splitting. The renderer's auto-height behavior preserves text but does not make a tall image a physically small index card. Use `vision_analyze` for exported non-browser PNGs and fix unreadable density rather than accepting a successful render alone.

PNG requires Pillow; SVG/text do not. Prefer actual package requirements over guessed installation commands. Keep existing file limits and pixel safety bounds; shorten or split excessive material instead of removing caps.

## 3. Build a readable gallery and PDF

Generate an escaped standalone HTML gallery from the same source. Set `lang="de"`, explicit page dimensions and print margins; use proper text, not a screenshot-only PDF. For long packs, increase page count or split sections before reducing the font. Retain a theme-appropriate but high-contrast background/ink combination.

Use the `pdf` skill's `references/browser-print.md` for Chromium printing, font/layout readiness, overflow measurements and final PDF verification. This workflow prints HTML directly with `Page.printToPDF`, preserving selectable text. Native JSON/PNG/SVG cards remain separate importable artifacts.

Inspect screenshots returned by `browser_exec` directly. For a poster preview, set a viewport tall enough to show the whole sheet, scroll that sheet into view and use `capture_screenshot()`. Crop out neighboring pages/browser margins when needed; do not publish a clipped viewport as though it were the complete card. Keep a unique copy of the preview because browser screenshot helper paths may be reused.

## 4. Validate, regenerate and package

1. Read the saved source back in code; verify exact definition count, unique IDs and requested type coverage. Verify card-section and PDF-page totals independently: four characters can legitimately occupy six pages.
2. Run v1 `validate` on each card. Check the canonical English Skill list, PC pyramid/Refresh accounting, Condensed one-point box capacities/marking policy and derived Physique/Will thresholds. Confirm normal Consequence slots start empty. Distinguish template placeholders from completed characters.
3. Parse SVGs and decode PNGs with real libraries. Check every HTML sheet's content against its footer and page bounds; inspect representative rendered output visually. Read back PDF text and page count.
4. Review narrative consistency separately from schema checks. Check relationships, goals, timelines, evidence/inference and alternate solutions. When source changes, regenerate **every derived format**, including the PDF and any preview; stale formats otherwise preserve mistakes already fixed in prose.
5. Package a README, full sources, per-definition JSON/text, card sections in PNG/SVG/JSON/text, gallery, PDF, reusable theme and a manifest. Include a clear GM-spoiler warning and any intentionally unresolved player-agreement point. Do not imply a specific destination-app import was tested unless it was.
6. Create the ZIP outside the packaged directory, exclude caches/interpreter environments and incidental build probes, then verify its member counts and integrity with `ZipFile.testzip()`. Do not overwrite an unrelated archive.
7. Deliver a short overview, the PDF, the complete ZIP and one native preview through `MEDIA:/absolute/path`. Avoid replaying the export process or flooding the chat with every format.

## Optional offline engine

For compatible inspiration/reproducibility, read the current generation README and pass the requested ruleset explicitly:

```sh
python -m cardmaker generate npc --ruleset condensed --tier supporting --genre fantasy --seed 42 --format draft --output SOURCE.json
python -m cardmaker project SOURCE.json --audience gm --detail full --format text
python -m cardmaker project SOURCE.json --audience public --format png --output PUBLIC.png
python -m cardmaker reroll SOURCE.json --group presentation --seed 9 --format draft --output NEXT.json
```

The retained software supplies a bounded original NPC/location library, not arbitrary natural-language content. A context note is not proof that its meaning was enforced. Use bespoke authoring for new genres, German content or unsupported templates rather than forcing a request into unrelated bundles. Keep generated semantic drafts separate from v1 render cards; store source plus seed and content/generator versions, not just a seed.

## UI/source security and regression checks

- Project public cards through the trusted engine allowlist. Raw draft responses are GM-workspace envelopes containing secrets even when the accompanying card is public; public-share only the projected card.
- Keep form edits separate from semantic source. Require explicit discard confirmation before replacing them; preserve canceled edits and label backups as source, not synchronized form state. Generic imported cards remain unfiltered and need manual visibility review.
- Prepare validation and both SVG/text response bodies before committing card fields, source, applied audience and previews together. Keep the old applied audience label while loading; otherwise a failed preview can leave secrets under a public label. Test both SVG and text fetch/body failures across generate/import/project/reroll, plus retries and cancellation.
- Bound JSON depth failure as well as body size. Convert decoder recursion errors to controlled HTTP 400 and test a payload deep enough to exercise the actual runtime while remaining under the size limit; verify a healthy request afterward.
- Preserve loopback/Host/Origin restrictions and explicit routes. A local browser UI is not automatically reachable on the user's computer; do not expose it publicly without authorization. Download card JSON and source before closing because the editor does not autosave.
- Test stochastic sources through a real JavaScript `JSON.parse`/`JSON.stringify` round trip before project, audience/detail changes, reroll and source reimport. Bound numeric seeds to JavaScript's safe-integer range and keep large/opaque seed values as strings; Python-only JSON tests or a fixed seed such as 42 do not expose browser precision loss. Include unseeded generation and presentation rerolls, plus explicit safe-range boundary and large numeric/string cases.
- For code changes use `terminal` to run `python -m unittest discover -s cardmaker -t . -v`, Python compilation, and JavaScript syntax checks as applicable. UI logic tests may use Node; this does not make Node a runtime requirement of the Python app.

---
name: fate-content-generator
description: Use when generating any kind of Fate RPG content.
version: 0.4.3
author: Jaxbee, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fate, rpg, generation, worldbuilding, scenarios, aspects, cards]
    related_skills: []
---

# Fate Content Generator

Create original, usable Fate content of any kind, from one aspect to a campaign framework. Gene authors bespoke content grounded in the user's setting and chosen rules; the existing Python cardmaker supplies optional editable graphical artifacts and a small offline NPC/location generator. Do not confuse this broad authoring skill with the narrower software engine.

## When to use
- Generate, develop, revise or adapt any Fate RPG content: characters, NPCs, adversaries, creatures, locations, factions, organizations, items, vehicles, powers, extras, aspects, skills, approaches, stunts, scenes, challenges, contests, conflicts, mysteries, adventures, scenarios, settings, campaigns, hooks, clues or random tables.
- Produce an individual idea, a connected collection, a reusable content generator, or a rules-compatible game aid.
- Continue supporting graphical note cards and system-neutral adaptations when requested.
- Do not invent earlier agreements, uncommitted campaign lore, or existing character facts.

## Language and rules defaults

Generate content in **German**, with **English Fate terminology**. This applies to prose, aspect phrases, stunt names/descriptions, motivations, clues, dialogue, hooks and graphical exports. Keep field labels and mechanical terms in English: `High Concept`, `Trouble`, `Relationship`, `Aspects`, `Skills`, `Stunts`, `Physical Stress`, `Mental Stress`, `Consequences`, `Refresh`, `Fate Points`, `Overcome`, `Create an Advantage`, `Attack`, `Defend`, `Invoke`, `Compel`, `Boost`, `Free Invoke`, `Concession`, `Taken Out`, and severity/ladder labels. Keep canonical skill names (e.g. `Fight`, `Notice`, `Will`, `Academics`, `Lore`) and identifiers/JSON keys in English. Proper names already established by the user stay unchanged. Example: `High Concept: Ermittlerin mit einem Gedächtnis für fremde Schulden`; `Stunt: Kein Detail entgeht mir — +2 auf Notice für Create an Advantage, wenn ...`. English content requires an explicit request; do not mistake an English chat message for a language override. This policy concerns generated game content, not the language of ordinary conversation with the user.

**Fate Condensed is the baseline**, not Core or Accelerated. Use the Condensed skill list, including separate `Academics` and `Lore`, and Condensed Stress/Consequences rules. Switch systems only when the user explicitly asks; never silently mix in Core's escalating Stress boxes, Core phase-trio assumptions, or FAE Approaches. For full characters use `High Concept`, `Trouble`, `Relationship` to another PC (or an agreed placeholder), and two free Aspects. Standard separate Stress tracks contain one-point boxes, with several boxes markable for one hit; do not render `[1][2][3]` as default Condensed Stress. Consult the focused character-template reference below before selecting durability or complexity.

## Character base templates

Use [Condensed character templates](references/condensed-character-templates.md) and its four reusable JSON templates for people/creatures with character-like roles:

- **Goon / Mook** (`templates/characters/goon.json`): a minimal Condensed minor NPC, not a full sheet.
- **Standard NPC** (`templates/characters/standard-npc.json`): an everyday, distinct person; default a better-described minor NPC, not a mandatory Core supporting-NPC port.
- **Full Character / PC** (`templates/characters/full-character.json`): developed personality and full Condensed character sheet.
- **Major Opponent / BBEG** (`templates/characters/major-opponent.json`): Condensed major NPC with agenda, influence, methods, counterplay and concession/exit logic as well as appropriate stats.

These are **project base templates**, not four official Condensed NPC tiers. Condensed distinguishes minor and major NPCs; PC is a player-character build. Templates contain clearly marked placeholders and illustrative allocations, not finished campaign characters or a compulsory universal skill assignment. Preserve their mechanics policy, then customize fictional details and role-appropriate Skills. If Skills change, recompute Stress and domain-restricted bonus mild slots. Escalate an everyday NPC's mechanics only when their role in play warrants it, not merely because they have a name. For a follow-up request such as 'another bundle', retain the most recently agreed scope: use these four character tiers unless the user explicitly requests a wider content set. Do not resurrect an earlier all-content showcase merely because it exists in the conversation.

## Scope and zoom: fill blanks, do not write the user's plot

**Do not invent an overarching story, conspiracy, main quest, shared crisis, faction struggle, deadline or campaign arc unless the user asks for one.** A genre/theme or a request for a bundle is not permission to manufacture a connected plot. The user supplies the main story; generate usable local texture around it. Ordinary places and people may simply exist and do their jobs. An Aspect or interesting detail is not an obligation to add a secret or adventure hook.

- **Town request:** stay at overview level: brief identity, named buildings/functions, broad layout if useful. At most one casually mentioned person per building, and only when useful. Do not expand every proprietor into a cast or add a town-wide Hook/current crisis as a default ending.
- **Specific building request:** zoom into that building. Give its owner/proprietor, a few relevant staff and perhaps a regular customer; each needs only a name, role and one easy-to-play trait. Add a compact layout, what is available there, and one or two ordinary details. Do not create full NPC sheets, secret agendas or Skill blocks for everyone unless asked.
- **Local connections are welcome:** relatives, coworkers, neighbors, regular customers and mundane favors make places feel lived-in. Example: the saloon owner is the barber's father. Keep the relationship local; do not turn it into a dynasty, mystery or faction plot.
- **Respect the requested zoom:** a request for a saloon is not a request for the town's main adventure. A request for a town is not a request to fully populate each room. More detail should follow a follow-up request, not preempt it.
- If the user requests context, a story arc or integration with supplied canon, then make those explicit connections without overwriting their plot. Otherwise leave narrative slots open rather than filling them with unsolicited hooks.
- Short personality cues, useful features, everyday friction and modest relationships are enough to avoid blandness. Do not replace an unwanted main plot with several covert miniature plots or insist on Want/Obstacle/Secret/Countdown fields on every entry.

## Complexity budget: disposable means disposable

Low-tier content must be instantly playable, skimmable and disposable—not miniature PC sheets or scenario essays. This takes priority over longer generic authoring checklists and export conventions.

- **Goon / Mook:** name/type plus at most **four short fields**, roughly **40 German words total**: one Aspect, one relevant Skill (occasionally two), `Stress` with 0–1 one-point boxes, and one terse behaviour/break cue. A generic designation is enough. No mandatory Goal, Trouble, secret, relationship, boundary, tactics essay or dedicated portrait page. Do not print absent Stunts/Consequences/Refresh, rule explanations or GM-pool reminders. Keep zero Consequences and no Stunts in underlying metadata.
- **Standard NPC:** at most **five short fields**, roughly **65 German words total**: role/one Aspect, one or two relevant Skills only if useful, and one concrete Want/Offer/Hook. A single mannerism may help; omit it if redundant. Show Stress only when conflict is expected; no automatic secrets, backstory, relationship web or separate sections for every personality dimension. Extra depth is opt-in or promotion to a full character, not a consequence of having a name.
- **Other incidental material:** a simple shop, item, clue or hazard gets only the facts needed to use it now. Do not manufacture a web of motives, mechanics or connections merely to fill a template.
- Keep details for Full Character/PC and Major Opponent/BBEG. Do not apply their complexity to extras. Put shared rules and caveats in one optional reference, never repeat them on disposable cards. Printed minor-NPC stats use `Aspect`, `Skills`, `Stress` and perhaps `Behaviour`, not compulsory High Concept/Trouble/Relationship blocks.
- Bundle Goons and low-detail NPCs together on a compact sheet; never give each a mostly empty full page or repeat scenario setup on their cards. For minor-only requests, concise chat text or one small card is the default; PDF/ZIP/galleries are optional rather than mandatory.

## Procedure
1. Establish the task's scope from the request: content type, intended use, level of detail and delivery format. Retrieve relevant campaign notes when available; preserve established facts, names and discoveries. Treat new material as proposals until adopted. Use sensible defaults rather than interrogating the user about every field.
2. Use **Fate Condensed** before generating mechanics, unless the user explicitly requests another ruleset/hack. Treat older Core demonstrations and the preserved legacy cardmaker instructions as examples, not standing defaults. Use the four Condensed base templates for character content; an unknown party's strength is not permission to call a BBEG balanced. Distinguish descriptive characteristics from Skills and any explicitly requested optional attribute/Approach hack.
3. Load [Fate rules guardrails](references/fate-generation-presets.md) for mechanical work and [NPC/location authoring](references/npc-location-authoring.md) for people/place content. Consult the relevant primary SRD section when extending beyond researched material; do not imply the NPC/location research already validates every possible Fate subsystem. Label original house rules and optional modules clearly.
4. Establish only the fiction needed at the requested zoom. For an incidental town, building, person or item, provide identity, immediate use and a little local texture. Ordinary relationships are optional; a broader causal situation, opposition, pressure, secret, stakes or consequence chain belongs only in content that actually needs it or when the user requests narrative context. Do not infer permission to write a main plot from a genre/theme or bundle request.
5. Use the type-specific checks below, then write the requested content itself, not merely an outline of how to create it. Add only useful mechanics; an ordinary place or object need not become a full character. Keep quantities and complexity appropriate to narrative importance.
6. Review coherence, player agency, aspect playability, rules correctness, visibility and table usability. Do not claim encounter balance without relevant PC and scene context. Separate GM secrets from public material. Maintain alternate discovery opportunities for necessary conclusions without moving established facts retroactively.
7. Deliver in the most useful requested format: concise text, structured source, graphical cards, scene outline, relationship/zone diagram or longer document. Treat a requested theme as fictional tone and visual direction, not automatic permission for connected goals or an adventure: create original local material, not merely recolored old content. Add a shared plot only if asked. For explicitly requested downloadable themed bundles, provide a readable PDF, editable JSON, copyable text, individual PNG/SVG cards and a ZIP, with one inline graphical preview. Respect the low-tier complexity budget: combine incidental entries on compact sheets, and do not force these export formats onto a simple Goon/NPC request. Split complex PC/BBEG material into Profile/Mechanics and Stunts/GM Notes instead of shrinking everything onto one card. Count character definitions separately from card sections and PDF pages. Follow [card and bundle exports](references/cardmaker-workflow.md) for the rendering and packaging sequence. If an executable generator/tool is requested, implement and exercise it rather than presenting templates as working software.
8. For a multi-type showcase or 'one of each', derive the exact types from the user's referenced list, save an index/manifest and verify uniqueness and completeness programmatically. Prefer a shared demonstration setting when useful, explicitly not campaign canon; a shared setting does not require a shared story arc. Clearly isolate optional skill-list changes and alternative-ruleset examples rather than adding them silently to the main character sheets. Provide editable sources plus a readable gallery/PDF when useful; check every layout for overflow.

## Content-specific checks

- **PCs and important characters:** concept, trouble, distinct aspects, relationships and goals; chosen skill/approach model, scoped stunts and correctly derived stress/consequence slots when requested. Do not generate past injuries as ordinary empty slots.
- **NPCs, creatures and adversaries:** first choose the complexity budget above. Goons need only a role/Aspect, minimal stats and one usable behaviour cue; ordinary NPCs need one practical hook, not a biography. Reserve the richer want/obstacle/offer/boundary/connection/tactics/concession checklist for developed or major characters. Tier is not morality. Low-tier opposition is deliberately disposable.
- **Locations and environments:** match the requested zoom. Towns get named buildings/functions and optional single local faces; specific buildings get a proprietor, a few staff/regulars, a compact layout and everyday flavor. One usable feature or optional Aspect is often enough. Do not force pressure, danger, opportunities, secrets, zones or a town-wide Hook into ordinary places. Add these only when requested or inherent to the location's stated purpose. Locations remain statless by default; active scene setup and location-as-character mechanics are explicit expansions.
- **Factions and organizations:** agenda, methods, resources, faces, relationships, internal tension and next move absent intervention. Mechanize influence or opposition only when useful; label custom systems.
- **Items, powers, vehicles and extras:** fictional identity and permissions, capabilities, limits/costs, meaningful complications and relevant aspects. Add stunts, competencies or stress only to support their role. Label proposed permissions/costs and rule exceptions for table approval.
- **Aspects and stunts:** clear specific aspect phrases with useful and complicating applications; no automatic permanent +2. Stunts state competency, action, circumstance, effect and applicable cost/frequency/limit. Keep invoke examples, hostile invokes and compels distinct.
- **Scenes and encounters:** framing, participants, goals/stakes, opposition, usable aspects, zones/routes where needed and multiple approaches. Pick a challenge, contest or conflict based on the fiction rather than making everything combat. No predetermined player decisions.
- **Mysteries, adventures and scenarios:** situations and motivated actors, actionable hooks, useful secrets, clues and plausible discovery channels, interconnected nodes, escalation and possible consequences. Separate observable evidence from inference, intent and authorship; state any fictional legal/procedural rule needed to justify a conclusion rather than making physical evidence prove too much. Give linked escalation events one consistent order and propagate changes to every affected actor/location/scene. Preserve freedom of approach; redundant paths to essential conclusions, not one mandatory check.
- **Settings and campaigns:** premise, tone, themes, current/impending issues, factions/faces/places, PC connections, open questions and a playable starting situation. Separate adopted canon from proposed additions; expand incrementally instead of scripting a fixed plot.
- **Random tables and reusable generators:** define purpose, inputs, constraints, coherent selection groups, output schema, originality/provenance and quality tests. Randomness should create useful surprise, not incompatible traits. Save seed plus content/generator version for reproducibility when implemented.

## Optional cardmaker workflow

Locate the `fate-has-no-mercy` checkout and work from its repository root. Read `cardmaker/README.md` for commands, dependencies and supported schemas. The [card and bundle workflow](references/cardmaker-workflow.md) covers source preparation, rendering, themed layouts, packaging and UI/source safety checks.

For bespoke content, write v1 card JSON with `write_file`: `version`, `kind`, `title`, optional `subtitle`, `tags`, ordered `fields` of `label`/`value`. Supported render kinds: `npc`, `location`, `character`, `item`, `faction`, `note`. Map other concepts such as vehicles/extras to an appropriate generic kind without inventing unsupported enum values. From the repo root use `terminal`:

- `python -m cardmaker render CARD.json --format text`
- `python -m cardmaker render CARD.json --format svg --output CARD.svg`
- `python -m cardmaker render CARD.json --format png --output CARD.png`

Inspect graphical output with `vision_analyze`; fix clipping/density and rerender. Deliver images/documents with `MEDIA:/absolute/path`. Keep editable structured source. Use companion cards or GM notes for long content instead of unreadable text.

The **offline CLI/UI generator still generates NPC/location drafts only**, from nine original fantasy/noir/scifi situation bundles. It does not implement arbitrary Fate content generation or NLP constraint enforcement. Use bespoke authoring for other content and campaign-specific requests; do not force them into these bundles or pretend `--context` enforces lore. Full semantic source is separate and GM-only. Only supported draft projection can automatically create an allowlisted public card; manually authored generic cards require deliberate public/GM separation and inspection.

## Pitfalls

- Broad skill coverage is authoring capability, not a claim that every subsystem or content type is implemented in Python or already researched exhaustively.
- The current offline engine's English content library and historical defaults do not satisfy this skill's German/Condensed policy automatically. Pass `--ruleset condensed` explicitly when using it, then author/localize and inspect German card content while retaining English mechanics; prefer bespoke generation from the four templates. Do not claim new language or four-template controls were implemented in the Python UI/CLI merely because skill templates exist.
- Do not conflate Core, Condensed, Accelerated and custom hacks. No default Strength/Dexterity layer, HP conversion or private NPC fate-point purse.
- Optional Fate fractal mechanics are a design choice, not a requirement that everything have a character sheet; the current offline generator does not support them.
- Generic card imports are unfiltered; raw draft backups contain secrets even alongside a public preview. Form edits are not synchronized to semantic drafts.
- Keep player agency and meaningful counterplay. Avoid scripted choices, stereotype shortcuts and copied proprietary random tables.
- Do not commit/push campaign material, expose a local server or change another profile without authorization.

## Verification

Check every stated constraint and output type, established facts, entity references, rules profile, numerical derivations and secrecy. Enforce the minor-NPC word/field budgets; remove filler, repeated rules and empty sections. A short entry that can be played immediately is better than a complete-looking but cumbersome low-tier sheet. Verify German content with unchanged English Fate keywords/Skill names, selected Condensed template, one-point Stress boxes and marking policy, derived Physique/Will thresholds, empty Consequences and PC Refresh/Stunt accounting. Use tools for calculations and unfamiliar rules. Generated proposals are not evidence of existing campaign facts.

For graphical cards confirm real successful exports and inspect them. For software changes use strict TDD and the checkout's test runner: `python -m unittest discover -s cardmaker -t . -v`; exercise CLI and live HTTP/browser paths as applicable. Preserve the UI's atomic card/source/audience/preview transitions and controlled JSON-depth errors, described in the retained workflow. Report tested results and any limits plainly.

# Practical NPC and location generator research

## Scope and evidence quality

Ten substantive sources were read: six designer-practice articles, three working generators, and one publisher's description of its free/deluxe game tools. Perchance was an additional blocked lead, not a successfully tested generator. This is qualitative interface inspection, not a reliability benchmark or a review of private backends.

All recommendations below are our implementation synthesis, not claims that a source supplies an existing algorithm. No proprietary random tables were copied. The repository was not modified.

**Retrieval warning:** `web_extract` returned article bodies ending mid-sentence after roughly a few thousand characters even when given a much larger character limit. Its JSON responses are retained as partial retrievals only. Full designer articles were subsequently fetched with direct HTTP, saved with raw HTML, and converted to text with a stdlib HTML parser. Browser text and screenshots support generator observations. A final read/ledger-list command encountered an approval gate; it was not retried.

## Designer sources and exact supporting excerpts

### Universal NPC Roleplaying Template — Justin Alexander

URL: https://thealexandrian.net/wordpress/37916/roleplaying-games/universal-npc-roleplaying-template

Provenance: direct HTTP 200; complete HTML and parsed page text in `direct-01.json` / `direct-01.txt`; article dated October 11, 2015. Original extraction `extract-01.json` was incomplete.

Exact short excerpts:
- “Roleplaying: This is the heart of the template, but it should also be the shortest section.”
- “You’ll generally only need one mannerism. Maybe two.”
- “Rather than burying that clue in the narrative of the NPC’s background, you’re yanking it and placing it in a list to make sure you don’t lose track of it during play.”

Finding: separate first-impression appearance, optional quote, tiny playable mannerism/personality notes, relevant background, and key information. It explicitly puts optional system stats last. Structured retrieval at the table matters more than biography volume.[1]

Implementation: front-load an immediately playable impression and a concrete desire; put what the NPC knows/offers in a separately labeled GM field. Voice should be an executable cue (short clauses, answering with questions, measured pauses), not an essay or a mandatory ethnic accent.

### Memorable NPCs — Justin Alexander

URL: https://thealexandrian.net/wordpress/43539/roleplaying-games/random-gm-tip-memorable-npcs

Provenance: direct HTTP 200; `direct-08.json` / `direct-08.txt`; article dated August 28, 2019.

Exact short excerpts:
- “Give the NPC a strong agenda. Make them want something.”
- “It actually works best if this agenda is not aimed directly at the PCs.”
- “Have NPCs connected to each other and give them strong, contradictory opinions about each other.”

Finding: an agenda that overlaps the PCs' interests feels less like an NPC existing solely to issue a quest. Relationships and differing justified opinions create playable ambiguity; the author also recommends reusing existing NPCs and explains why agenda tables depend strongly on setting context.[11]

Implementation: generate `want + obstacle + resource + relationship` together. Let an existing campaign NPC fill a role instead of always inventing a new person. An optional competing loyalty should complicate the same agenda, rather than add unrelated traits.

### Types of Nodes — Justin Alexander

URL: https://thealexandrian.net/wordpress/8049/roleplaying-games/node-based-scenario-design-part-9-types-of-nodes

Provenance: direct HTTP 200; `direct-02.json` / `direct-02.txt`; dated June 14, 2010. Initial extraction was incomplete.

Exact short excerpts:
- “In my experience, nodes are most useful when they’re modular and self-contained.”
- “Spread a few clues leading to other macro-nodes within each network of sub-nodes and you can achieve highly complex intrigues from simple, easy-to-use building blocks.”

Finding: useful nodes include places, people, organizations, events, and activities; smaller nodes can live inside larger ones. Scope should fit what the GM actually needs, not maximal geographic or biographical detail.[2]

Implementation: cards are nodes with stable IDs and references. A location may contain zones and point to an NPC or faction, but a single card should not become an entire setting gazetteer. A hook/clue should point somewhere actionable rather than merely hint at undefined mystery.

### Don't Prep Plots — Justin Alexander

URL: https://thealexandrian.net/wordpress/4147/roleplaying-games/dont-prep-plots

Provenance: direct HTTP 200; `direct-09.json` / `direct-09.txt`; dated March 23, 2009.

Exact short excerpts:
- “Don’t prep plots, prep situations.”
- “For any conclusion you want the PCs to make, include at least three clues.”

Finding: prepare circumstances, goal-oriented opponents, and reusable resources instead of a required sequence of PC actions. The three-clue principle concerns needed conclusions and chokepoints; it is not a requirement to print three clues on every incidental card.[12]

Implementation: describe what happens if nobody intervenes, what actors want, and what tools they have. Never write “the PCs agree,” “the players must,” or a single inevitable solution into generated hooks. Campaign-level validation can count independent clue routes for necessary revelations.

### Secrets and Clues — Michael E. Shea / Sly Flourish

URL: https://slyflourish.com/sharing_secrets.html

Provenance: direct HTTP 200; `direct-03.json` / `direct-03.txt`; dated March 28, 2016. Full text includes the later section “Secrets Aren't Drivers, They're Fuel,” absent from the initial partial extract.

Exact short excerpts:
- “Secrets aren't an entire story. They're not complete pictures.”
- “If they miss the check the secret may come up some other way.”
- “We don't use secrets to steer the direction of the PCs.”

Finding: useful, compact information fuels player-chosen action. Shea prepares secrets without committing to one delivery vehicle, allowing their revelation wherever it makes sense; not every prepared secret must appear.[3]

Implementation: represent a secret's **fact** separately from optional **discovery channels** and **why it matters**. A card can suggest physical evidence, a witness, or an observable inconsistency without declaring one mandatory gate. Do not move an already established fact to contradict play. A rumor's truth status belongs in GM-only data.

### Location Moves — Michael E. Shea / Sly Flourish

URL: https://slyflourish.com/location_moves.html

Provenance: direct HTTP 200; `direct-04.json` / `direct-04.txt`; dated January 12, 2026. The saved parsed text has encoding artifacts in some dash characters; raw HTML is retained.

Exact short excerpts:
- “These locations can do things. These locations have \"moves\".”
- “Do the characters or NPCs trigger them by doing something or moving somewhere?”
- “You can end effects a few ways as well.”

Finding: evocative location features become dynamic when they act, have triggers, and can change or end. The article warns against effects that continually prevent characters from escaping.[7]

Implementation: `feature + interaction + trigger + consequence + counterplay`. Make a hanging bridge both a route and a risk; a sluice gate can flood a zone or drain it. Distinguish danger from opportunity. Avoid unavoidable punishment disguised as scenery. Keep numeric mechanics out of system-neutral mode.

## Actual generator comparisons

### donjon Fantasy Random Generator — exercised

URL: https://donjon.bin.sh/fantasy/random/#type=npc

Provenance: live browser DOM/text. Saved `donjon-before.txt`, `donjon-human-after.txt`, `donjon-location-after.txt`, `donjon-controls.json`.

Exact interface excerpts: “Random Locations”, “NPCs”, “Any Gender”, “Any Race”, “Any Class”, “Generate”.[4]

Actions verified: loaded NPC mode; changed the visible ancestry selector to Human; clicked Generate; received a new batch of NPCs labeled Human. Changed to Random Locations, selected in Town, and generated another batch. These are exercised outputs, not inferred backend functionality.

Strengths observed: fast batches; a small number of genre-relevant controls; NPC output combines a name, gender/ancestry/class/alignment, appearance/equipment, and an additional personality/goal/detail sentence. Location output sometimes adds a sensory cue or current threat.

Limits of inspected output: many entries remain independent seeds, not a connected cast; some additional sentences supply only a trait or companion rather than a desire. The tested human batch contained the name Cyne twice, illustrating why a local connected-cast generator should check duplicate identifiers/names. No claim is made that other donjon tools lack richer features. Backend implementation and offline operation were not tested.

Product lesson: keep one-click batch generation and bounded controls, but add shared situation/entity references and meaningful reasons to act. Do not import alignment, binary gender controls, attractiveness judgments, or culture-to-morality associations into the neutral schema.

### Chaotic Shiny Character Generator — exercised

URL: https://chaoticshiny.com/chargen.php

Provenance: live browser text before and after clicking “Meet someone new”; `chaotic-before.txt`, `chaotic-after.txt`. The web extractor returned almost none of the visible content.

Exact interface excerpts: “Meet someone new”, “Motivation:”, “Current Mood:”, “Competence:”, “Sucker for:”, “Annoyed by:”, “Hobby:”.[5]

Actions verified: inspected a full generated profile and clicked its reroll link; a different named profile appeared. The profile exposed motivation, class, mood, appearance, competence, weapon, preferences, and satisfaction percentages.

Strengths observed: compact labeled fields make the result easy to skim; the separation of motivation and mood is useful. Weakness in the inspected profiles: motivation can be a broad noun rather than a concrete immediate objective, and the many independent details do not explain one another. This is an assessment of two observed profiles, not a claim about every possible result. Backend, probability distributions, and bulk reliability remain untested.

Product lesson: preserve structured skimmability, not the field count. Replace personality diagnostics/attractiveness/sin percentages with a specific objective, an obstacle, an offer, and a pressure point. A compassionate but cynical bodyguard could be coherent, but the generator must supply the connecting circumstance rather than simply hope the GM invents it.

### Watabou Village Generator — exercised

Project URL: https://watabou.itch.io/village-generator
Working tool: https://watabou.github.io/village-generator/

Provenance: complete direct HTTP project page in `watabou-project-full.json` / `.txt`; browser rendered canvas, URL capture, context menu, Parameters dialog, and reroll. Saved `watabou-menu.png`, `watabou-rerolled.png`, `watabou-parameters.png`, `watabou-url.txt`, `watabou-rerolled-url.txt`.

Exact observed menu labels: “New village”, “Reroll village”, “Parameters...”, “Layers”, “Style...”, “Export as”. Exact parameter labels visible in the screenshot include “grove”, “isolated”, “no square”, “river”, “crossroads”, “palisade”, and “Generate”. The project page says “Made with Haxe + OpenFL.”[6]

Actions verified: generated a village map containing roads, fields, buildings, river, and bridges; opened its right-click menu; used Reroll village; saw a changed settlement layout/population while the original seed and terrain tags remained in the URL and a `roads` value was added; opened its parameter dialog. The canvas UI required screenshot inspection; empty body text was not evidence of an empty generator.

Strengths observed: configurable constraints and a separate settlement reroll preserve useful context. The map makes routes and spatial relations visible rather than listing unrelated location names. Export **menu availability** was observed, but no export was downloaded or validated. Seed round-trip determinism was not tested. Backend and source licensing were not audited.

Product lesson: expose constrained rerolls and retain locked context. A cardmaker need not clone a map generator: an explicit small zone/connection graph provides its own useful spatial affordance. A map alone does not supply the cast's motives or discoverable secrets; the inspected screen was spatial, not an NPC narrative engine.

## Legitimately available free tools: what was and wasn't read

### Worlds Without Number — Sine Nomine publisher description

URL: https://sine-nomine-publishing.myshopify.com/products/worlds-without-number-deluxe-pdf
Official free-edition listing discovered: https://www.drivethrurpg.com/en/product/348809/worlds-without-number-free-edition

Provenance: complete publisher page HTTP 200, `direct-07.json` / `.txt`. This is a publisher product description, **not a read of the book's tables**. Direct retrieval of a related storefront mirror was blocked (`direct-05.*`); no purchased material or unverified third-party PDF was used.

Exact short excerpts:
- “It's packed solid with system-neutral GM tools and worldbuilding support”
- “And those contents are in the free edition of the game!”
- “a sheaf of bonus GM tables for fleshing out architecture, NPC relationships, and random adventure NPCs.”

Finding: the publisher describes faction rules, adventure creation tools, and worldbuilding tags as included in the free edition; the additional architecture/NPC relationship/random-adventure-NPC tables appear in the **deluxe additions**, not the preceding free-content list.[10]

Implementation: learn the general separation of setting tools from system mechanics, but author original situation bundles and content. Free availability does not itself grant redistribution rights. Do not claim to have inspected or ported WWN tables, and do not promise deluxe table coverage as a free feature.

## Blocked lead, not a fair functional comparison

Perchance example: https://perchance.org/dnd-npc-generator-custom

Direct request returned HTTP 403; real browser showed Cloudflare “Performing security verification” instead of the generator. Saved `direct-06.json` / `.txt` and `perchance-host.txt`. A search snippet suggested controls, but it is not a tested interface and is not used to assess its coherence, quality, backend, API requirements, or licensing. Do not generalize this one inaccessible community generator to the whole Perchance platform.

Red Markets was not added merely to meet a count: no verified designer passage was retrieved in this sweep. SWN book tables likewise were not read; the publisher's WWN discussion references SWN, which does not make that an independent SWN source.

## Synthesis: coherence instead of random trait soup

The core design recommendation is a **small causal situation model**, not a larger adjective dictionary. This is our synthesis of context-dependent agendas, modular connected nodes, compact useful information, and interactive locations.[11][2][3][7]

1. Begin with explicit context: genre/technology/magic bounds, tone, environment, scale, existing names/factions, and excluded themes. Hard constraints are distinct from soft stylistic preferences.
2. Choose an original situation bundle: a needed resource, two parties with competing claims, an obstruction, and a change that happens without intervention. These components establish causal commitments.
3. Derive NPC agenda, obstacle, bargaining resource, relationship, useful knowledge, and visible behavior from those commitments. Keep one unrelated humanizing detail if it helps, not a dozen.
4. Derive the place's original/current purpose, sensory anchors, manipulable features, occupants, routes/zones, current danger, opportunity, and clues from the same commitments.
5. Add bounded variation after the causal core is stable. Tension is not contradiction: an honest official concealing a debt is interesting when there is a reason; unexplained incompatible jobs, locations, or technologies are generator errors.
6. Hooks expose stakes and options. Secrets reveal leverage, routes, hazards, or competing interpretations. Neither dictates the party's decision.

### Suggested compact NPC schema

`id`, `name`, `role`, `first_impression`, `voice_cue`, `want`, `obstacle`, `can_offer`, `leverage_or_boundary`, `relationship_refs`, `secret_fact`, `discovery_options`, `hook`, `gm_notes`.

- Want is a verb plus concrete object, not “greed”.
- Leverage is not necessarily blackmail: an unmet need, promise, evidence, favor, duty, or principled red line can matter.
- Relationships identify another named entity and explain the connection. Opinions may differ without making one identity group intrinsically good/evil.
- Voice cue describes delivery or vocabulary; no requirement to perform an accent.
- Keep public/read-aloud fields separate from GM-only information.

### Suggested compact location schema

`id`, `name`, `kind`, `purpose_then_now`, `sensory_anchors`, `features`, `zones_and_edges`, `occupant_or_faction_refs`, `current_pressure`, `danger_with_warning`, `opportunity`, `secret_fact`, `discovery_options`, `outbound_refs`, `gm_notes`.

- Use two or three sharply chosen sensory anchors, not exhaustive sensory checklists. At least one should relate to something actionable.
- Features pair a concrete object with a possible interaction and consequence. Let players discover other uses.
- A small location can have three named zones and explicit connections; do not label everything a Fate zone unless the system mode calls for it.
- Danger needs a warning/trigger and some counterplay. Opportunity must be useful independently of killing an occupant.
- Clues point to an entity, route, useful conclusion, or changed decision. “Something feels wrong” alone is atmosphere, not an actionable clue.

These schemas are recommendations, not transcriptions of any proprietary template or table.

## Prioritized local Python / no-API implementation

### P0 — useful, coherent, reproducible

1. Preserve the existing import/render pipeline; add generation as an upstream producer of its established data format. A migration adapter is safer than breaking old saved cards.
2. Implement a stdlib-compatible deterministic generator using a local `random.Random(seed)` instance, stable entity IDs, and versioned original content bundles. Store seed plus generator/content version with output. Reproduction across content changes requires saving the generated document, not only the seed.
3. Add explicit context filters and coherent bundle selection. Reject impossible combinations or conflicting locked fields with a useful error instead of silently overwriting user input.
4. Generate connected NPC/location pairs or a small cast with shared names, factions, resources, secrets, and references. Validate references, self-relations, and duplicate display names before rendering.
5. Give each NPC a concrete want/obstacle/offer and each location an interaction/danger/opportunity. Put key actionable information outside descriptive prose.
6. Keep system-neutral data mechanically neutral. Fate-compatible display can label narrative aspects and optional zones through an adapter; do not invent Fate numeric balance from generic adjectives.

### P1 — editing and quality gates

7. Allow selective reroll by coherent group, not only whole-card reroll. Lock name/context/cast while rerolling presentation; changing the situation must regenerate dependent agenda/secret/hook fields together. Show when locks conflict.
8. Offer compact card and extended GM-note views. Render fields with per-field length budgets and visible overflow warnings; never silently clip the only clue or a relationship target. Escape arbitrary imported text.
9. Test reproducibility, multiple seeds, hard context constraints, missing optional fields, Unicode names, valid entity references, preserved locked fields, empty eligible bundles, and backwards-compatible import/render. Golden snapshot tests are useful, but also assert semantic contracts.
10. Add content review checks against identity-to-morality mapping, disability as automatic menace, poverty/foreignness as danger shorthand, and attraction or gender as personality substitutes. This is a proposed safety/quality policy, not an assertion that every inspected generator does these things.

### P2 — richer campaign support

11. A small optional graph view or printable connection index can show locations/zones/people/factions without implementing a full map engine.
12. At campaign scale, validate alternate routes to essential revelations rather than demanding three redundant clues on every card. Track known facts and discoveries so a reroll cannot retcon established play.
13. Support user-authored local content packs with a schema, validation, explicit provenance/license metadata, and original examples. Do not ship scraped generator output as an unlicensed dataset.

## Agent-authoring skill priorities

The future card-authoring skill should instruct an agent to:

1. Read the actual renderer/import schema and content budget before writing; inspect existing campaign canon and reuse names when appropriate.
2. Obtain enough context to constrain output, but use sensible defaults for a new neutral setting rather than interrogating the user about every field.
3. Draft the shared situation first, then derive a small linked cast and place. Explain each NPC's want, obstacle, offer, boundary, relationship, and useful knowledge in playable language.
4. Turn every location feature into something a character can inspect, manipulate, exploit, avoid, bargain over, or learn from. Name sensory evidence, routes, factions, danger, opportunity, and discoverable information.
5. Write secrets as facts with plausible channels and implications, not instructions that players must follow. Provide choices and consequences; do not script outcomes.
6. Keep public/GM information distinct and optional Fate mechanics distinct from neutral content. Reject stereotype shortcuts and overstuffed backstories.
7. Run the real local CLI, render the artifact, inspect output/overflow, and validate import compatibility and entity references. Do not claim “generated” when only prose or a plan exists.
8. Save provenance for borrowed design principles; use original authored content rather than copying proprietary tables. Mark inaccessible or untested sources plainly.

## Sources

This local report uses task-local ledger IDs only. Parent reports should register URLs and evidence themselves instead of copying these numbers.

[1] https://thealexandrian.net/wordpress/37916/roleplaying-games/universal-npc-roleplaying-template
[2] https://thealexandrian.net/wordpress/8049/roleplaying-games/node-based-scenario-design-part-9-types-of-nodes
[3] https://slyflourish.com/sharing_secrets.html
[4] https://donjon.bin.sh/fantasy/random
[5] https://chaoticshiny.com/chargen.php
[6] https://watabou.itch.io/village-generator
[7] https://slyflourish.com/location_moves.html
[10] https://sine-nomine-publishing.myshopify.com/products/worlds-without-number-deluxe-pdf
[11] https://thealexandrian.net/wordpress/43539/roleplaying-games/random-gm-tip-memorable-npcs
[12] https://thealexandrian.net/wordpress/4147/roleplaying-games/dont-prep-plots

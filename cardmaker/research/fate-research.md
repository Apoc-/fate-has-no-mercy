# Fate generator research: rules boundaries and engineering recommendations

## Outcome and scope

**Recommendation:** add a fiction-first authoring layer with explicit Core / Condensed / Accelerated presets, then project its structured output into the existing version-1 `kind/title/subtitle/tags/fields` card contract. Default locations to **statless places or scene setups**, not characters. Make numeric location mechanics an explicit, labeled opt-in.

Research corpus: full direct-fetch HTML and complete `<main>` text for 22 Fate SRD pages, including 21 substantive rules/advice pages and the official licensing page. All substantive pages were read in full. Additionally, the official CC-BY SRD archive was downloaded and relevant NPC/stress/fractal sections cross-checked in its Core, Accelerated, Condensed and System Toolkit documents; the entire books were not claimed as fully read. `manifest.json` and `official-package-manifest.json` record provenance; `evidence.json` / `evidence.md` contain 69 short, exact, programmatically checked excerpts. URLs below are raw for parent-agent merging; local ledger numbers are deliberately not used here.

Official redistributable package: https://fate-srd.com/downloads/CC-BY-SRDs.zip

Read-only local context: `cardmaker/README.md`, `schema.json`, and the example NPC/location JSON. No repository files modified. Recommendations below are design proposals, not existing generator capabilities or campaign canon.

## 1. Rules and evidence that should drive the design

### NPC complexity follows narrative role, not whether someone has a name

Core distinguishes nameless, supporting and main NPCs, but expressly permits minimal sheets: “you’re never obligated to give any [NPC] a full sheet like the ones the [PC]s have.” It also says giving someone a name and motive need not improve their durability. Generate only encounter-relevant details and support promotion without replacing established fiction. Core supporting NPCs normally have high concept, trouble, additional aspects, a stunt, a small skill column, two stress tracks, mild consequence and optionally moderate; its own examples vary, so treat the recipe as a preset rather than a universal validity law. Main NPCs are PC-like, can be drafted incompletely, and may exceed ordinary starting-PC limits.

https://fate-srd.com/fate-core/creating-and-playing-opposition

Condensed instead names **minor** and **major** NPCs. Minor NPCs get only needed aspects and one or two relevant skills, potentially custom descriptive competencies; they may have a stunt, zero to three stress boxes, and generally no consequences. Exact excerpt: “For a minor NPC, only define what is absolutely necessary.” Major NPCs can be PC-like; exceptional threats can break normal character limits. Do not present Core’s supporting tier as a named Condensed rule.

https://fate-srd.com/fate-condensed/being-game-master

Accelerated distinguishes PC-like important/recurring opposition and lightweight mooks. Mooks use descriptive strengths at +2, weaknesses at −2 and an unlisted default of +0, rather than needing six approaches. They have one or two aspects, zero to two stress boxes and no consequences: “Mooks can’t take consequences.” Its grouped-mook procedure is distinct from Core teamwork mobs; it assigns a stress box per two individuals. Do not silently combine both bonuses and durability procedures. The text does not specify rounding for odd-sized groups; offer even group sizes or label an explicit project rounding choice.

https://fate-srd.com/fate-accelerated/being-gamemaster

### Skills, approaches, and attributes are not interchangeable defaults

Core skills describe broad competencies. Condensed likewise uses skills, but its default list separates mundane **Academics** from supernatural **Lore**. FAE approaches answer how a task is done: “Approaches are descriptions of how you accomplish tasks.” Its six default approaches are Careful, Clever, Flashy, Forceful, Quick and Sneaky, with starting allocation +3, +2, +2, +1, +1, +0. This is a starting-character preset, not a cap on every major adversary.

https://fate-srd.com/fate-core/skills-stunts
https://fate-srd.com/fate-condensed/getting-started
https://fate-srd.com/fate-accelerated/who-do-you-want-be

A D&D-like Strength/Dexterity/etc. attribute array is **not** a default shared Fate component. Condensed lists attribute-based alternatives under optional skill-list changes. Support `custom_competencies` or a named hack profile, not a second automatic numeric layer on top of Fate skills. Ordinary fictional descriptors—appearance, manner, occupation, motive—can still be called descriptive attributes without becoming game statistics.

https://fate-srd.com/fate-condensed/optional-rules

### Stress needs an explicit policy, not a single integer called HP

- **Core:** ordinary full characters start with separate physical and mental tracks containing capacities `[1,2]`. Mark at most one box per hit. Physique / Will lengthen their respective tracks: ratings +1/+2 add the third box; +3 or above add the fourth; +5 or above also grant a domain-restricted extra mild consequence. Nameless NPC durability uses its own recipe; do not accidentally apply full-PC stress bonuses to every mook with Physique.
- **Condensed:** ordinary full characters start with two tracks of three **one-point** boxes; several boxes can absorb one hit. Relevant ratings +1/+2 give four boxes, +3 or higher six; +5 or higher additionally grants the restricted mild consequence. Minor-NPC stress is its separate zero-to-three-box recipe. Alternate/unified tracks are adjustments, not the default.
- **Accelerated:** ordinary full characters use a single `[1,2,3]` track and mark one box per hit. Approaches do not define Physique/Will-derived track increases. Mooks shorten the track under the GM recipe; show capacities and policy explicitly rather than ambiguous circles or a total.

Exact cross-version warning: “With 1-point stress boxes you may mark as many of them as you want when you get hit”; the same Condensed section contrasts Core’s one-box-per-hit rule.

https://fate-srd.com/fate-core/stress-consequences
https://fate-srd.com/fate-core/resolving-attacks
https://fate-srd.com/fate-condensed/getting-started
https://fate-srd.com/fate-accelerated/ouch-damage-stress-and-consequences

Ordinary full sheets share mild/moderate/severe consequence capacities of 2/4/6; these are **slots for new harm aspects**, not pre-generated injuries. Normal slots are shared across harm domains; high-skill bonus mild slots can be restricted. Core also includes an extreme-consequence last resort that replaces an existing non-high-concept aspect; it is not an ordinary fourth reusable slot. Condensed explicitly makes extreme consequences optional. FAE mild recovery can occur at scene end with rest, unlike Core/Condensed’s treatment-plus-subsequent-scene procedure. Never apply one global recovery policy across the three profiles.

https://fate-srd.com/fate-core/resolving-attacks
https://fate-srd.com/fate-condensed/challenges-conflicts-and-contests
https://fate-srd.com/fate-condensed/optional-rules
https://fate-srd.com/fate-accelerated/ouch-damage-stress-and-consequences

### Aspects should produce decisions and playable affordances

Core’s concise quality rule: “The best aspects are double-edged, say more than one thing, and keep the phrasing simple.” Its suggested test is two beneficial uses and two hostile uses/compels. This is advice, not a required mechanical tax on every simple mook or scene aspect; Core explicitly says scene aspects need less breadth.

https://fate-srd.com/fate-core/making-good-aspect

Aspects are fictional truths even without a payment, but not permanent free numerical bonuses. Condensed says they “can grant or withdraw permission for what can happen in the story”. A compel introduces a real complication, not merely a forced miss; hostile invokes and compels are different operations. Boosts are special temporary benefits and cannot simply be treated as normal compellable aspects.

https://fate-srd.com/fate-condensed/aspects-and-fate-points

**Generator consequence:** for important aspects generate short optional `help_example`, `complication_example`, and `fictional_permission` notes. Do not output an automatic +2 next to every aspect. An original proposal such as **“Dock Union Fixer, Still Owes the Smugglers”** offers contacts and leverage but also a demand that compromises a rescue; this is more actionable than “Mysterious” or “Charismatic.”

### Locations have three distinct modes

1. **Place reference:** identity, atmosphere, significance, people and hooks. No mechanics required—not even aspects. Core’s explicit statement is “Unlike [NPC]s, they don’t require aspects.”
2. **Scene setup:** a place in use now, with participants, stakes and a few situation aspects; optionally zones and passive difficulties. Core recommends three to five evocative aspects and usually two to four zones for conflicts, but explicitly permits omitting aspects/zones in many mental conflicts. Condensed similarly recommends compact maps and allows aspects scoped to individual zones. These are useful defaults, not minimum requirements on every tavern or conversation.
3. **Fractal threat / location-as-character:** explicit opt-in when the site, storm, machine or organization needs to act, resist or change under sustained pressure. Core’s permission is “Anything can have aspects, skills, stunts, stress tracks, and consequences **if you need it to**” (emphasis added). The Toolkit permits custom relevant competencies instead of humanoid skills. A sentient fortress might have Surveillance and Sealed Passages; an ordinary inn needs neither Will nor mental stress.

https://fate-srd.com/fate-core/faces-places
https://fate-srd.com/fate-core/setting-scene
https://fate-srd.com/fate-condensed/challenges-conflicts-and-contests
https://fate-srd.com/fate-core/extras
https://fate-srd.com/fate-system-toolkit/bronze-rule

Do not equate every fractal write-up with a player-owned extra. Core’s extras include controlled locations and carry their own permission/cost considerations. Likewise, do not turn every statless obstacle into an attackable enemy. Condensed’s optional obstacle framework distinguishes hazards, blocks and distractions by function; countdowns have a track, trigger(s), and outcome. These are **optional modules**, not mandatory location statistics.

https://fate-srd.com/fate-core/extras
https://fate-srd.com/fate-condensed/optional-rules

### Opposition should expose purpose and counterplay, not promise encounter balance

Core says “Right-sizing the opposition is more of an art than a science”. Its relative-skill and opposition-number advice is guidance, not a challenge-rating formula. Record PC count, relevant PC peak, intent and desired intensity when available; otherwise label assumptions rather than inventing a balanced threat. Core specifically asks what an opponent needs, how PCs can help or obstruct it, and why it cannot be ignored.

https://fate-srd.com/fate-core/creating-and-playing-opposition
https://fate-srd.com/fate-core/establish-opposition

Use a passive difficulty when the fiction needs an obstacle, active opposition when a character can meaningfully interfere, and no roll when nothing interesting opposes the action. A chase or race may be a contest, not an HP fight; conflicts require participants able and willing to harm one another. Default scene aspects do not automatically grant free invokes—Condensed expressly leaves setup free invokes to GM judgment. Group/teamwork policy must be profile-specific: Condensed caps combined-skill support at the leader’s skill.

https://fate-srd.com/fate-core/actions-outcomes
https://fate-srd.com/fate-condensed/challenges-conflicts-and-contests

### Stunts should be structured and bounded

Generate a special action/skill substitution, a scoped bonus, or a limited rule exception. Prefer a named ability, action, circumstance, effect, and any frequency/cost limit. Core cautions: “You don’t want a stunt replacing the skill it modifies.” Core also prohibits stunt exceptions that rewrite the basic aspect/fate-point economy. FAE provides bonus and once-per-session exception templates; this does not make all stunts once-per-session or require every stunt to cost a fate point.

https://fate-srd.com/fate-core/building-stunts
https://fate-srd.com/fate-condensed/getting-started
https://fate-srd.com/fate-accelerated/stunts

## 2. Proposed generator data model — engineering design, not Fate rules

Keep two layers: **semantic draft** for validation and regeneration, and **v1 render card** as a deterministic projection. Existing generic fields remain unchanged. Use an extension object or separate source file for semantics; README warns the current form edits only documented fields, so preserve semantic source independently and do not trust the UI to maintain an executable round trip.

Suggested semantic entities:

- `GeneratorRequest`: `kind`, `ruleset`, `rules_profile_id`, `preset_id`, `completeness` (`quick/full/partial`), setting/tone constraints, allowed content, supplied canon, linked entity IDs, optional `pc_count` / `pc_peak` / `scene_intent`, `seed`, generator/content-pack versions.
- `NPCDraft`: stable ID, name, role, descriptive appearance/manner, immediate goal, need, pressure, relationship, leverage, why PCs care, concession/exit idea; `tier` and separate `allegiance` / `opposition_function`. A supporting ally is not inherently a boss.
- `Aspect`: text, category, scope (`character/place/scene/zone`), optional zone ID, example use/complication, visibility. Separate enduring place features from temporary scene state.
- `Competencies`: tagged union of `skills`, `approaches`, `descriptive_strengths_weaknesses`, or `custom`; named integer ratings plus explicit default. Never require skills and approaches simultaneously without a labeled hybrid profile.
- `Stunt`: name, rationale, type, relevant competency, permitted action(s), circumstance, bonus or effect, limit/cost, table-review flag. Keep authored prose alongside machine-readable constraints.
- `StressTrack`: harm domain, ordered box capacities, `mark_policy` (`one_box_per_hit` / `multiple_boxes_per_hit`), derivation policy. Keep checked state separate from the reusable template.
- `ConsequenceSlot`: severity, capacity, allowed domains; aspect initially absent. Extreme consequence is a separate last-resort rule, not an ordinary injury slot. Distinguish disabled mechanics, no slots, and intentionally unfinished slots.
- `LocationDraft`: mode (`place/scene/fractal`), identity/significance, atmosphere, usable features, inhabitants/faces, pressure and opportunities; optional scene participants/stakes, scoped aspects and zone graph. Only `fractal` enables a deliberate mechanics bundle.
- `ZoneGraph`: IDs, short names, edges with access/line-of-sight/impediment notes, scoped aspect references. No mandatory grid, exact feet or miniatures simulation.
- `OppositionElement`: tagged `passive_difficulty/active_actor/optional_hazard/optional_block/optional_distraction`; goal, trigger, counterplay, failure cost. Keep countdowns as distinct optional objects, not stress.
- `Provenance`: generated proposal vs supplied fact, source/profile IDs, preserved user edits and canonical locks. Sources establish mechanics, not proof that invented NPCs exist in the campaign.

**Projection order:** identity/role → concept/trouble/aspects → motive/relationship/leverage → competencies → stunt(s) → explicit stress/consequence labels → tactics/concession. Location cards: atmosphere/significance → situation aspects if any → interactive features → people/pressure → zones/opposition if enabled → hooks. Put large main-NPC mechanics on a companion card rather than burying a usable hook beneath a long stat block.

## 3. Preset policy

These are proposed selectable defaults; allow explicit overrides and incomplete authoring.

- **Core mook:** native nameless recipe; choose Average/Fair/Good subtype, one or two aspects, a few role-relevant skills, short shared stress or none, no ordinary consequences. Keep the subtype’s skill/stress recipe together. Optional mob mode must use Core’s own teamwork/overflow approach rather than FAE group rules.
- **Core supporting:** high concept + trouble + useful extra aspect(s), roughly four or five relevant skills as a column, one useful stunt, two derived Core tracks, mild consequence; optional moderate for durability. Warn on unusual departures rather than rejecting authored exceptions.
- **Core main:** PC-like full or intentionally partial sheet; ordinary default of five aspects, campaign-appropriate skill shape, relevant stunts, derived tracks and ordinary consequences, plus explicitly represented Core extreme-consequence option. Require explicit campaign assumptions for elevated skill caps.
- **Condensed mook:** map UI label to native **minor**; concise aspect(s), one or two normal or descriptive skills, optional stunt, zero-to-three one-point stress boxes, generally no consequences.
- **Condensed supporting:** label **project convenience preset**, not an official third tier. Offer a fleshed-out minor or deliberately reduced major; explicitly state chosen stress/consequence policy rather than copying Core numbers invisibly.
- **Condensed main:** native **major**; PC-like default skills/aspects/stunts and Condensed stress policy, with threat overrides allowed. Keep conditions, scale, countdowns, extreme consequences, and boss-rule breaks off until selected. Do not automatically assign each NPC a private starting-PC fate-point budget; Condensed GM spending uses a scene pool.
- **FAE mook:** descriptive +2 / −2 / 0 competence bands, simple aspect(s), zero-to-two-box shortened FAE stress track, no consequences; separate optional grouped-mook variant.
- **FAE supporting:** label a project intermediate-detail preset. There is no separate named supporting-tier recipe in the cited FAE GM chapter. Use a clearly reduced important-NPC sheet, not an undocumented Core port.
- **FAE main:** six approaches with a PC-like starting distribution unless campaign difficulty justifies explicit changes, high concept/trouble plus further aspects (three to five filled at start), one unified escalating track, ordinary consequence slots, scoped stunts. One starting stunt is the beginner-friendly default, with later filling/free-stunt options rather than an arbitrary compulsory three.
- **Location place:** no required aspects, skills, stress, consequences or zones. Prefer significance, a face, interactive feature and pressure/hook.
- **Location scene:** a few useful situation aspects, optional compact zone graph, participants, stakes and context-specific obstacles. Default free invokes to zero unless explicit preparation or GM choice establishes otherwise; this is a conservative generator choice, not a rules prohibition.
- **Location fractal:** opt-in label and rationale, only relevant custom competencies, optional tracks with stated meaning and defeat/transition conditions; do not auto-populate every character component.

## 4. Validation and quality rubric

**Hard errors (structure/policy):** missing selected rules profile; mixed competency models without declared hybrid; noninteger ratings; invalid action types; malformed box capacities; incompatible stress marking policy; missing zone references; illegal control characters or v1 payload size; silently discarded authored facts; ordinary consequences on a strict no-consequence mook preset; location mechanics present while explicitly in statless mode. An explicit custom profile may permit otherwise unusual mechanics.

**Warnings (quality or soft defaults):** five synonymous aspects; all bonuses/no complications; unclear aspect referent; motive disconnected from scene; universal +2 stunt; rare stunt trigger irrelevant to setting; no counterplay or noncombat option; a giant zone graph; more aspects than fit the requested card; unexplained elevated NPC peak; missing PC context despite a “balanced” label; optional module without an opt-in. Counts such as three-to-five scene aspects are not universal hard validity rules.

**Proposed review score, 0–2 per dimension:** (1) clear identity and table readability; (2) motive/stakes/why care; (3) playable aspect opportunities; (4) rules-profile correctness; (5) meaningful player choice/counterplay; (6) connected people/place fiction without contradictions; (7) distinctiveness and variation; (8) compactness and completeness appropriate to tier. Release target: no hard errors, full score for rules correctness, and at least 12/16 overall. This threshold is a project acceptance recommendation, not an official Fate metric.

**Acceptance-test ideas:** seeded generation produces identical semantic and v1 output; preserve locked facts when rerolling one section; promotion preserves identity/relationships; main sheets derive stress correctly at skill thresholds; Core rejects marking two boxes for one hit while Condensed permits it; FAE never derives stress from Forceful; minor/mook templates do not accidentally inherit PC tracks; locations can legitimately contain no mechanics; optional modules stay absent by default; consequences begin as empty slots; printed fields and semantic data agree. A seed alone is insufficient for reproducibility if content packs change—persist profile and generator versions too.

## 5. Retrieval and licensing cautions

`web_extract` repeatedly returned bodies ending around 3,000 characters even with a generous budget. Those results were not treated as complete pages. Direct stdlib `urllib` fetches plus an HTML parser recovered complete SRD `<main>` sections; original HTML and unabridged text are retained. Python `requests` was unavailable, so no dependency installation was necessary. Direct Evil Hat product-page access returned HTTP 403; a later `web_extract` recovered its relevant overview/change section, but that page was not used as a counted full source or as evidence for this report.

The SRD website is a presentation of the rules, not the exact official redistributable source file. Its official licensing page says: “Do not use the text on this site, as we have made changes to present the system better as a website.” This matters if shipping copied rules text or templates: obtain the official SRD package and comply with its chosen license/attribution. Paraphrase procedural recommendations and generate original card fiction; do not bundle copied rule tables or imply official certification.

https://fate-srd.com/official-licensing-fate

Remaining judgment calls: relative encounter difficulty is context-dependent; optional/hack profiles need table approval; FAE odd-sized mook-group rounding is not specified by the cited chapter; semantic metadata round trips through the current form need implementation-time testing. No generator implementation, dependency changes, or repository writes were performed.

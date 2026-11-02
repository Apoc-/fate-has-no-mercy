# NPC and location generation: research and implementation

## Executive conclusion

A useful generator should produce a **playable situation**, not a long list of unrelated traits. The implemented engine now generates a linked NPC and location around one shared issue, then projects the selected entity into the existing editable card format. It remains local, deterministic when seeded, and free of external AI/API requirements. Gene can also author bespoke cards when the small offline library does not fit a request.

The research covers Fate Core, Condensed, Accelerated and optional fractal advice; designer practice from Justin Alexander and Sly Flourish; and exercised interfaces from donjon, Chaotic Shiny and Watabou. Detailed source-by-source reports and evidence are in `fate-research.md`, `practice-research.md`, `fate-evidence.json` and `practice-provenance.json`. Source IDs in the two specialist reports belong to their own ledgers; they are not one merged numbering scheme. This overview uses direct source links instead.

Local `source_file`/`path` values in the research records are historical retrieval locations on the research host, not portable checkout paths or bundled source files. Use the recorded public URLs to retrieve sources; those local caches are not required to run Cardmaker.

## 1. What makes an NPC usable?

### Agenda before biography

Justin Alexander recommends a strong agenda that need not be aimed at the PCs, plus relationships and differing opinions. His roleplaying template separates a short performable cue and key information from background. These are reasons to make someone act, not merely labels such as mysterious, greedy or charismatic. See [Memorable NPCs](https://thealexandrian.net/wordpress/43539/roleplaying-games/random-gm-tip-memorable-npcs) and the [Universal NPC Roleplaying Template](https://thealexandrian.net/wordpress/37916/roleplaying-games/universal-npc-roleplaying-template).

Our resulting authoring checklist:

- A clear name/role and one visible first impression.
- A concrete immediate objective: a verb, an object and a reason it matters now.
- An obstacle linked to the same situation, rather than a second unrelated problem.
- A useful offer or resource; a boundary or pressure point that shapes negotiation.
- A named relationship that connects the NPC to the place or another interest.
- One voice/manner cue the GM can perform without an accent or caricature.
- Useful knowledge separated from descriptive prose.
- Where conflict is plausible, an exit or concession option besides death.

Not every actor needs every detail on the visible card. Complexity should follow their role in play. An ally can have a strong agenda; a named person can remain mechanically lightweight. Fate Core expressly distinguishes nameless, supporting and main NPCs while saying a full PC-style sheet is never obligatory. See [Creating and Playing the Opposition](https://fate-srd.com/fate-core/creating-and-playing-opposition).

### Situations, not scripts

[Don't Prep Plots](https://thealexandrian.net/wordpress/4147/roleplaying-games/dont-prep-plots) argues for situations rather than prescribed player action sequences. Our design therefore describes who wants what, available resources, current pressure and open choices. It does not decide that the party agrees, follows one lead, attacks an occupant or reaches an inevitable conclusion.

The causal structure is:

`issue/resource → competing interests → obstacle → pressure → NPC goal/offer/boundary → location affordances → possible player choices`

This is our engineering synthesis, not an algorithm supplied verbatim by any source.

## 2. What makes a location playable?

### Interaction matters more than exhaustive description

[Location Moves](https://slyflourish.com/location_moves.html) treats locations as things that can do something, with triggers and ways for their effects to change/end. [Types of Nodes](https://thealexandrian.net/wordpress/8049/roleplaying-games/node-based-scenario-design-part-9-types-of-nodes) emphasizes modular, usable nodes rather than an undifferentiated mass of setting notes.

Our location checklist:

- Purpose/significance and two sharply chosen sensory anchors.
- At least two concrete features with possible interactions.
- A face or faction and a current pressure.
- A danger with a visible warning, trigger, consequence and counterplay.
- An opportunity independent of killing whoever is present.
- Information that can change a decision, not merely atmosphere.
- When needed, a small connected route/zone graph with access notes.

Example of the distinction: “an old sluice gate” is scenery. A counterweight players can brace, a bypass they can drain, a skipping chain that warns of a surge, and competing water claims create choices. The feature remains useful even if the players invent a solution the generator did not name.

### A place is not automatically a combatant

[Fate Core: Faces and Places](https://fate-srd.com/fate-core/faces-places) says places do not require aspects. [Setting the Scene](https://fate-srd.com/fate-core/setting-scene) suggests a compact number of aspects and zones when preparing conflicts, but does not mandate a zone map for every conversation. [Extras](https://fate-srd.com/fate-core/extras) permits applying character components to other things **if needed**.

The implemented distinction is:

- **Place:** statless reference; purpose, people, useful features, pressure and opportunities.
- **Scene:** the place in active use; stakes, three connected zones, scoped situation aspects for Fate profiles, and an illustrative passive obstacle.
- **Fractal/location-as-character:** researched but deliberately **not implemented**. A sentient fortress or storm can warrant custom competencies and stress, but a tavern should not automatically receive Will, mental stress and consequence slots.

The scene counts and sample +2 obstacle are explicit project defaults, not universal Fate requirements or an encounter-balance promise.

## 3. Secrets, clues and player agency

[Sly Flourish: Secrets and Clues](https://slyflourish.com/sharing_secrets.html) treats secrets as useful information that fuels player choices, not instructions steering them along a plotted route. A failed delivery opportunity need not permanently eliminate access to information.

Our semantic source separates:

- **Fact:** what is actually true.
- **Discovery channels:** plausible evidence, a witness, or an observable discrepancy.
- **Implication:** why learning it changes leverage, routes or risk.

The original bundles provide several possible channels. These are suggestions, not mandatory skill-check gates. Already established facts should not move retroactively to contradict play. Necessary campaign revelations deserve redundant access, but three clues on every incidental card would be needless clutter.

GM secrets, hidden objectives and source metadata are not automatically safe to share with players. The generator uses public-field allowlists, not label-based filtering. Generic old cards lack reliable visibility metadata and remain unfiltered with a warning. Raw draft backups are always GM material.

## 4. Fate aspects and attributes: the important boundaries

### Aspects should invite play

[Making a Good Aspect](https://fate-srd.com/fate-core/making-good-aspect) recommends clear, double-edged aspects that say more than one thing, and suggests testing beneficial and complicating applications. The guidance is more demanding for enduring character/game aspects than short-lived situation aspects.

The engine supplies aspect text plus situation-related help and complication examples. Full GM projection includes these examples; compact projection omits the explanatory text rather than clipping it. Aspects are not automatic permanent +2 modifiers. Stunts are separate scoped proposals, marked for table review, with an action, competency, circumstance and limit.

For bespoke authoring, “Keeper of Water That Others Claim” offers more potential play than “Competent.” It can establish expertise or access while exposing obligations and competing claims. This is original example phrasing, not a copied rule table.

### Do not blend rulesets

The following distinctions come from the native SRDs; see the specialist report for exact excerpts and official-package cross-checks:

- **Core** uses skills and nameless/supporting/main NPC roles. Full-style characters have separate physical/mental escalating stress tracks; at most one box absorbs a hit. Physique and Will affect their tracks. Nameless NPCs use their own lighter recipes. Sources: [Opposition](https://fate-srd.com/fate-core/creating-and-playing-opposition), [Stress and Consequences](https://fate-srd.com/fate-core/stress-consequences), [Resolving Attacks](https://fate-srd.com/fate-core/resolving-attacks).
- **Condensed** names minor/major NPCs. Full-style tracks use one-point boxes, several of which can absorb a hit. The supporting UI preset is explicitly a reduced-major project convenience, not a third native tier. Its skill list distinguishes Academics from supernatural Lore. Sources: [Being the Game Master](https://fate-srd.com/fate-condensed/being-game-master), [Getting Started](https://fate-srd.com/fate-condensed/getting-started).
- **Accelerated** uses approaches for important NPCs and descriptive +2 strengths/−2 weaknesses for lightweight mooks. Full-style characters have a unified escalating track; approaches do not grant Physique/Will-derived extra boxes. The intermediate supporting option is a project convenience. Sources: [Being the Gamemaster](https://fate-srd.com/fate-accelerated/being-gamemaster), [Who Do You Want To Be?](https://fate-srd.com/fate-accelerated/who-do-you-want-be), [Stress and Consequences](https://fate-srd.com/fate-accelerated/ouch-damage-stress-and-consequences).
- **Neutral** output has descriptive characteristics, not invented numeric attributes or Fate mechanics.

Strength/Dexterity-style attributes are not an extra default layer shared by all Fate games. Alternate skill/attribute designs are optional hacks. See [Condensed Optional Rules](https://fate-srd.com/fate-condensed/optional-rules). Requested custom hacks should be labeled and authored explicitly, not silently stacked on skills or approaches.

Consequences are empty harm-aspect slots, not generated existing wounds. Stress is represented as box capacities plus a marking policy, not HP. Ordinary NPCs are not assigned a private PC-like fate-point purse. Without PC/context information the tool does not call an encounter balanced.

## 5. Existing generators: what we actually learned

These are qualitative interface observations, not backend audits or probability/reliability benchmarks. The companion practice report records actions, saved outputs and limits.

### donjon

[Fantasy Random Generator](https://donjon.bin.sh/fantasy/random/#type=npc) was exercised with a Human NPC filter and town-location generation. It provides fast batches with a small number of useful controls. The inspected outputs mainly supplied independent seeds rather than a linked cast. Lesson adopted: keep quick constrained generation, but connect agendas, places and useful information. Other donjon tools were not exhaustively reviewed.

### Chaotic Shiny

[Character Generator](https://chaoticshiny.com/chargen.php) was loaded and rerolled. Labeled fields are easy to skim, but the observed profiles contained broad motivation nouns and many details whose causal connection remained for the GM to supply. Lesson adopted: a smaller want/obstacle/offer/relationship model is preferable to accumulating diagnostic percentages or unrelated adjectives.

### Watabou

[Village Generator](https://watabou.itch.io/village-generator) was inspected via its creator page and working canvas tool. Reroll and parameters were exercised. Constraint controls and spatial connections are useful ideas. Our engine uses a small graph and conservative presentation rerolls, not a map engine. Watabou export-menu presence was observed, but downloaded exports and seed replay were not verified.

### Eigengrau

The [creator's design document](https://github.com/ryceg/Eigengrau-s-Essential-Establishment-Generator/wiki/Game-Design-Document) describes a contiguous town with NPCs referencing one another and setting context influencing generation. That architectural claim comes from documentation; its live generator was not independently exercised in this task. The useful lesson is connected entities and context, not copying its implementation or content.

### Coverage limits

- Perchance's tested community generator was blocked by Cloudflare, so it is not functionally ranked.
- The Worlds Without Number publisher description was read, not its book tables. The description separates free worldbuilding/adventure support from deluxe additions including extra architecture/relationship/NPC tables. Free access does not establish redistribution rights. See the [publisher page](https://sine-nomine-publishing.myshopify.com/products/worlds-without-number-deluxe-pdf).
- No proprietary random tables or harvested generator outputs were bundled as our content.

## 6. What was implemented

- A real local content generator upstream of the old renderer.
- Nine original coherent bundles: three each for fantasy, noir and science fiction.
- Linked NPC/location semantic source with stable source-local IDs and explicit references.
- Deterministic seeded generation, recorded generator/content versions and separate full-source backup.
- Ruleset-specific NPC tiers, aspects, skills/approaches/competence bands, scoped stunt proposals, stress policies and empty consequence slots.
- Statless place vs active scene modes.
- CLI generation, source projection and conservative presentation reroll.
- Python-served UI generation, import, projection, editing and exports.
- Explicit GM/public and compact/full views; raw-source export prohibited as a public CLI format and disabled in public UI view.
- Name locks, preserved context notes/canon notes, controlled validation errors and existing local-only HTTP security.
- Original generic JSON rendering and dark/parchment themes remain compatible.

Commands and exact contracts are in `../README.md`.

## 7. Honest limitations and next priorities

The implemented generator is a bounded original content library, not a general natural-language story model. All current bundles emphasize resource disputes and pressured custodians; they do **not** yet represent broad occupational, moral or encounter diversity. Gene's bespoke authoring workflow is the appropriate route when a request does not fit. `--context` preserves an unparsed note but cannot enforce arbitrary lore. Name locks do not semantically transform a seed archivist into a guard or tavern keeper.

Presentation reroll preserves the causal situation, not a new situation or mechanic. It changes delivery/emphasis and sensory order. A seed is reproducible only within the recorded generator/content version; save the complete draft. The form edits a card projection, not the semantic draft: preserve edits as card JSON and source as a separate GM backup.

Full GM material can be tall. The renderer grows without clipping; it does not currently paginate a main NPC into several small print cards. Public handouts are shorter. Do not mistake compact projection for a fixed physical index-card layout.

Priorities for a next iteration:

1. Broaden original role/situation families: hospitality, deception, pursuit, wilderness, bargains, antagonists, ordinary social scenes and discovery—not only pressured stewards.
2. Add validated user content packs and explicit setting/role/tone constraints before promising richer procedural diversity.
3. Add multi-card print layouts and a companion GM-note export for main NPCs/complex scenes.
4. Support campaign-wide existing entity references, known discoveries and promotion without retcons.
5. Add fractal or alternate-attribute mechanics only with explicit profile schemas and table approval.

## 8. Research confidence and verification

Complete SRD pages and designer articles were retained because initial web extraction silently ended mid-section. Direct stdlib retrieval recovered the substantive text. The Fate researcher checked exact evidence excerpts and cross-checked relevant official redistributable SRD sections. The practical-generator findings distinguish exercised interfaces, read documentation and inaccessible leads.

A parent bulk citation-import/quote-check script did not run after an approval timeout; this overview therefore does not claim that a new merged evidence ledger passed verification. The existing specialist source records, exact excerpts and Fate verification manifest are retained. Technical generator testing and independent code review are recorded separately in the release verification artifact, not inferred from research quality.

When redistributing rule text, consult the [official licensing guidance](https://fate-srd.com/official-licensing-fate) and official source package, not merely the website's presentation. This project ships original fiction and paraphrased procedural mechanics, not scraped rule tables or official certification.

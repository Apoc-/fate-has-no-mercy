# Fate generator research guardrails

Use these when designing NPC/location authoring for cardmaker; they are research-backed design constraints, not a claim that a generator is implemented.

- Select an explicit Core, Condensed or Accelerated profile before generating mechanics. Core has nameless/supporting/main tiers; Condensed names minor/major; Accelerated uses mooks and important PC-like opposition. Label any intermediate tier added to the latter two as a project convenience.
- Model stress as ordered box capacities plus a marking policy, not HP. Core normally uses separate physical/mental escalating tracks with one box per hit; Condensed uses one-point boxes with several markable per hit; Accelerated normally has one unified escalating track. Preserve separate mook recipes and consequence policies.
- Default places to statless reference cards. Scene setup may add situation aspects, passive opposition and optional zones. Location-as-character is an explicit Fate-fractal opt-in, not a universal requirement. Even place aspects are not mandatory in Core game creation.
- Keep skills, approaches, descriptive mook competence bands and custom attributes as distinct competency models. Attributes such as Strength/Dexterity are optional alternate skill-list designs, not an extra default Fate stat layer.
- Treat aspect quality and suggested aspect/zone counts as advice. Test important aspects for useful invocations and meaningful complications; do not turn each aspect into a free permanent +2. Stunts need a scoped effect, applicable action/circumstance and any cost/frequency limit.
- Separate semantic source from the existing v1 generic card projection. The current editor only edits documented render fields; do not assume extension metadata is safely preserved by every editing route without testing.

Primary sources:
- https://fate-srd.com/fate-core/creating-and-playing-opposition
- https://fate-srd.com/fate-condensed/being-game-master
- https://fate-srd.com/fate-condensed/getting-started
- https://fate-srd.com/fate-accelerated/being-gamemaster
- https://fate-srd.com/fate-accelerated/ouch-damage-stress-and-consequences
- https://fate-srd.com/fate-core/faces-places
- https://fate-srd.com/fate-core/setting-scene
- https://fate-srd.com/fate-core/extras
- https://fate-srd.com/fate-core/making-good-aspect

For copied rule text use the official licensed package rather than website editorial text: https://fate-srd.com/official-licensing-fate and https://fate-srd.com/downloads/CC-BY-SRDs.zip . The archive includes standalone HTML SRDs, useful for checking primary wording without website adaptations.

## Local generator workflow

- Read the checkout's generation README before using `python -m cardmaker generate`; its engine supplies a deliberately small original bundle library, not free-form NLP generation. Treat `--context` as an exact unparsed constraint note and review contradictions yourself.
- Export `--format draft` as a GM-only source, then use `python -m cardmaker project SOURCE --audience public --format json|text|svg|png` for shareable views. Do not attach the raw semantic source to a public card; source carries secrets independently of the projected audience.
- Use `python -m cardmaker reroll SOURCE --group presentation --seed N --format draft` only for conservative delivery/emphasis changes; verify names, refs, causal facts, mechanics, original seed/content version and user canon notes remain unchanged. Unsupported reroll groups and unknown source versions should error, not silently reinterpret source.
- Exercise `python -m unittest cardmaker.test_generator cardmaker.test_cardmaker -v` after engine/CLI edits. Cover all genre/ruleset/tier combinations, not only neutral examples; compare public projection text against actual private facts/channels and run real CLI SVG/PNG exports.
- Validate a competency's stunt fiction as well as its numeric scope: a Contacts stunt should consult people or networks, not quietly perform a Crafts-only physical inspection.

Retrieval pitfall: web_extract can return a roughly 3,000-character body ending mid-section despite a larger char_limit. Check endings and retrieve complete HTML directly if needed. Stdlib urllib + HTMLParser can preserve full main text without requests/BeautifulSoup; retain original HTML, source URL, and exact quote-match checks.

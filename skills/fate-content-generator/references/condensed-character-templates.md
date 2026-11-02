# Fate Condensed: four character base templates

## User convention

Write generated fiction in German. Preserve English Fate field labels, canonical Skill names, action names and mechanical terms. Translate actual Aspect phrases and Stunt names/descriptions, not `High Concept`, `Trouble`, `Skills`, `Stress`, `Consequences`, `Refresh`, `Fight`, `Notice`, `Will`, etc. Existing proper names remain unchanged. All four templates explicitly use Fate Condensed. These authoring templates do not change the existing Python generator's interface or translate its old content packs automatically.

The JSON files in `templates/characters/` each contain a renderer-compatible v1 `card` plus `template` policy metadata. Export/render **the nested card**, not the wrapper. Replace all angle-bracket placeholders before calling it a finished character. Values are German and labels/keywords English. Numerical defaults are illustrative starting allocations; choose Skills to fit the actual role rather than forcing every PC into the demonstration's competence pattern.

## Shared mechanical rules

- Default Skill list: Academics, Athletics, Burglary, Contacts, Crafts, Deceive, Drive, Empathy, Fight, Investigate, Lore, Notice, Physique, Provoke, Rapport, Resources, Shoot, Stealth, Will. Academics covers ordinary knowledge; Lore covers arcane/supernatural knowledge. Do not substitute one for every appearance of the other automatically.
- Full PC/major-style sheets have separate Physical Stress and Mental Stress. At Physique/Will +0: three one-point boxes. At +1/+2: four. At +3/+4: six. At +5 or higher: six, plus an additional mild Consequence slot restricted to the corresponding harm domain. Track derivation is independent for each domain. Do not make a high Fight or Lore grant extra Stress.
- Boxes are all capacity 1 and several may absorb one hit. These are not HP. Never import Core's one-box-per-hit rule or `[1][2][3]` progression by accident.
- Full ordinary shared Consequences: mild 2, moderate 4, severe 6, initially empty. A +5 Physique/Will bonus mild slot is additional and domain-restricted, not a second unrestricted standard slot. Extreme Consequences are optional and disabled here.
- Minor NPCs use their own lightweight preset: zero to three one-point Stress boxes and generally no Consequences, not automatic full-PC tracks derived from their small Skill list.
- PC starting pyramid: one Skill +4, two +3, three +2, four +1; unlisted +0. Starting Refresh 3, three free Stunt slots, which can be left undefined. Each additional purchased Stunt costs 1 Refresh, minimum Refresh 1. No blanket +2 Stunt: name Skill, action and narrow circumstance; label authored rule exceptions for approval.
- NPCs use the GM scene Fate Point pool, not a separate PC-style Refresh purse. Boss exceptions must be explicit; stress, stunts or actions do not multiply merely because someone is called BBEG.

## 1. Goon / Mook

File: `templates/characters/goon.json`

Native Condensed category: **minor NPC**. Purpose: quick disposable opposition, not an elaborate personality essay. Default: one German identity Aspect under `High Concept`; one relevant Skill at +1 (example Fight); one one-point Stress box; no Consequences; no Stunts. A tougher goon may have a second Skill, another Aspect or up to three boxes; these are selections within the lightweight recipe, not mandatory upgrades.

**Printed output is capped at four short fields / about 40 German words including the heading:** `Aspect`, `Skills`, `Stress`, `Behaviour`. Combine current order and break cue into one brief Behaviour sentence. Do not print a biography, separate Goal/Appearance/Trouble/secret/relationship/boundary blocks, absent Stunts/Consequences, rule reminders or a GM advice essay. A generic designation is enough; one small entry, never its own full page. Goon does not mean stupid, immoral or automatically aggressive. Keep the fuller rule policy in metadata/reference only.

## 2. Standard NPC

File: `templates/characters/standard-npc.json`

Default native category: **minor NPC**, despite having a name. Keep the printed entry within five short fields / about 65 German words. Default to just `Aspect`, relevant `Skills`, and a concrete `Hook` combining Want/Offer. One mannerism is optional; show `Stress` only if conflict is expected. No mandatory Trouble, Boundary, backstory, secret, relationship network or empty Stunt/Consequence sections. Example mechanical metadata: Rapport +2, Notice +1, two one-point Stress boxes, no Consequences or Stunts. These are illustrative, not universal shopkeeper values. Extra development and Stunts require an actual need or explicit request.

Keep social competence, knowledge and resources appropriate to the person. Only promote to a major/reduced-major sheet deliberately when recurring conflict, durability or mechanical spotlight warrants it; do not call a Core supporting tier an official Condensed third tier.

## 3. Full Character / PC

File: `templates/characters/full-character.json`

Five Aspects: High Concept, Trouble, Relationship and two Free Aspects. Relationship connects to **another PC**; leave an explicit German agreement placeholder if no second PC exists instead of inventing a player character or using only an NPC connection as though it met the standard Relationship requirement. Add appearance/manner, Goal, Values/Boundary and a brief playable history; do not write the player's future choices for them.

Use the ten-Skill starting pyramid, three free Stunts or explicitly open slots, Refresh 3, derived Stress and shared empty Consequences. The sample allocation is an investigator/communicator (not an imposed class): Physique +1 and Will +2 therefore give four one-point boxes on each track. When making a warrior or different role, reassign the Skills and recalculate the tracks. Each filled Stunt must be situationally scoped. Clearly mark unfilled slots/placeholders; a template is not a finished playable build until completed.

## 4. Major Opponent / BBEG

File: `templates/characters/major-opponent.json`

Native category: **major NPC**. Give a High Concept, Trouble and further distinct Aspects, concrete Agenda, next move if unopposed, method, assets/allies, personal connection, two usable weaknesses/countermeasures and a Concession/Escape condition. It must work as a character, not a bag of inflated numbers. Harm is not the only way to oppose them; an influential antagonist may depend more on Contacts, Resources, Deceive or Will than Fight.

The template provides an **illustrative** higher-threat profile assuming relevant PC peaks near +4: apex +5; then two +4, three +3, four +2. That is an NPC design choice, not the PC starting pyramid, an official fixed boss recipe or a promise of balance. Ask/retrieve actual PC peak, party size, conflict type, supporting opposition and desired stakes before making a balance claim. Tune instead of blindly adding +1 to every stat. Default sample Physique +3 and Will +4 give six one-point boxes per track, with no bonus mild slot from its unrelated apex Skill.

Shared empty mild/moderate/severe slots; three narrowly scoped Stunt slots by default. More Stunts, extra durability or special actions are explicit, justified NPC exceptions rather than concealed PC Refresh accounting. No automatic extra turns, blanket immunity, forced mind-control or private Fate Point pool. Telegraphed strengths, defeat conditions, retreat and meaningful counterplay are required. A concession must be proposed before the relevant roll and negotiated; it preserves some agency, not automatic escape from already established consequences.

## Rendering and checking

1. Choose the template based on narrative/mechanical role, not just a proper name.
2. Fill German content while retaining English labels/Skill names. Complete placeholders or call the output a template.
3. If Skills change, calculate Stress and bonus mild slots. Check PC pyramid and Refresh accounting; do not impose PC limits on every major NPC.
4. Extract the `card` object and use the existing cardmaker renderer. Keep source and GM/private information distinct. Statless/public references need not expose secrets.
5. Verify all four files exist, IDs are unique, ruleset is `condensed`, narrative locale is `de`, terminology locale is `en`, Stress policies/capacities match, and the renderer produces real artifacts. A syntax check alone cannot judge the German prose or the usefulness of the character.

## Primary source basis

The relevant sections were read from the retained complete research copies and cross-checked during the earlier research against official SRD files:

- https://fate-srd.com/fate-condensed/getting-started — five Aspects and Relationship to a PC, default Skills, pyramid, Refresh, Stunts, Stress thresholds.
- https://fate-srd.com/fate-condensed/being-game-master — minor/major NPCs, lightweight Stress/Consequences, boss flexibility and shared GM Fate Point pool.
- https://fate-srd.com/fate-condensed/challenges-conflicts-and-contests — conflict, harm and Concession rules.

This reference supersedes older Core-default demonstrations and preserved legacy instructions for ordinary skill use. Explicit requests for other systems remain possible but must be labeled and kept separate.

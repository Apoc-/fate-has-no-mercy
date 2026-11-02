# Fate Has No Mercy

Fate RPG authoring resources, a local Python cardmaker, and the existing character sheet.

## Start here

- **Current authoring skill:** [`skills/fate-content-generator/SKILL.md`](skills/fate-content-generator/SKILL.md), including its references, character templates and Western palette.
- **Current town notes:** [`content/towns/fate.md`](content/towns/fate.md).
- **Specific building:** [`content/buildings/last-chance-saloon.md`](content/buildings/last-chance-saloon.md).
- **Code and usage:** [`cardmaker/README.md`](cardmaker/README.md).
- **Research and evidence:** [`cardmaker/research/README.md`](cardmaker/research/README.md).
- **Generated demonstrations:** [`content/examples/README.md`](content/examples/README.md).
- **Existing character sheet:** [`charsheet/charsheet.html`](charsheet/charsheet.html).

## Current conventions

The skill generates **German prose with English Fate terms and Skill names**, using **Fate Condensed** unless another ruleset is explicitly requested.

Four character templates cover Goon/Mook, Standard NPC, Full Character/PC and Major Opponent/BBEG. Minor content stays disposable: Goons have only a few short lines; everyday NPCs have a role and useful detail, not an obligatory biography or secret agenda. Towns remain high-level. A specific-building request expands its proprietor, a few staff/regulars, rooms and services. Local relationships are welcome; no overarching plot, conspiracy, main quest or deadline is added unless requested.

The skill is a **bespoke authoring workflow**, not a claim that the software implements every content type or preference. The standalone offline engine retains its smaller English NPC/location library and historical defaults. Pass `--ruleset condensed` explicitly when using that engine. It does not automatically localize content, enforce natural-language context notes, or expose the four skill templates as new UI controls.

## Run locally

Use Python 3.10+ from the repository root. SVG, text and the local HTTP editor use the standard library. PNG export additionally needs Pillow; see `cardmaker/requirements.txt`. The optional Node-based UI tests require Node, but the application does not.

```sh
python -m cardmaker --help
python -m cardmaker ui --host 127.0.0.1 --port 8765
python -m cardmaker render cardmaker/examples/npc.json --format text
```

The editor is loopback-only and does not autosave. Download card JSON and any separate GM source before closing it. A raw semantic source contains secrets even when its projected card is public. Generic authored cards are not automatically classified/redacted.

## Verify

```sh
python -m unittest discover -s cardmaker -t . -v
python -m compileall -q cardmaker
node --check cardmaker/app.js
```

Generated sample images/PDFs are included as demonstrations. They do not establish campaign canon or prove import compatibility with every external app. The existing character-sheet publishing workflow is unchanged; these additions are source/resources, not a new public app deployment.

## Skill snapshot

`skills/fate-content-generator/` is a portable repository snapshot of the installed authoring skill. Keep its `references/` and `templates/` alongside `SKILL.md`. It is not loaded by the Python application and is not automatically synchronized with a separate Hermes profile. Local machine paths have been removed from the committed skill entrypoint. See the official [Hermes Skills documentation](https://hermes-agent.nousresearch.com/docs/) for installation on another environment.

Older demonstrations preserve the design history, including the earlier Core showcase and the initially over-detailed Western minor NPCs. **Current skill/templates and the simplified low-tier examples take precedence** over those historical examples. Temporary browser/agent logs, interpreter caches, virtual environments and redundant ZIP archives are not part of this repository snapshot.

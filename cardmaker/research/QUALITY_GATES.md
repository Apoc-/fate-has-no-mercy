# Quality gates and review findings

## Research-derived content checks

Technical validation is necessary but does not prove narrative quality. Review each proposed NPC/location for a concrete reason to act, causal coherence, usable information, meaningful choices, and appropriate density. The first local library deliberately contains only nine original bundles and is not a general natural-language setting model.

Core, Condensed and Accelerated remain distinct profiles. Scene counts and sample difficulties are project presets, not universal mandates. Public data is a strict projected allowlist; raw semantic sources remain GM material.

## Parent verification before review

- Full unittest discovery passed 27 tests.
- Python compilation, JavaScript syntax and Git whitespace checks passed.
- A separate parent matrix exercised 720 drafts over rulesets, tiers, genres, modes and seeds, checking deterministic replay, valid sources, public redaction and presentation rerolls preserving the causal core.
- A real browser generated a named NPC and projected GM to public view. The public form omitted secrets and disabled raw source backup. PNG/SVG/text/JSON examples were actually rendered.
- Visual inspection found no clipping, but GM compact sheets remain tall. Fixed-size/paginated note-card layouts are not implemented.

## Independent failure-path review

The initial independent review correctly failed despite passing ordinary tests. Two reproduced defects required regression fixes before release:

1. A preview transport failure after changing audience could leave newly installed GM fields under a restored public selector. A secure transition must keep editor contents, preview/text, source association and view label consistent. Test both SVG failure and the later text-preview failure, not only happy-path redaction.
2. Deep JSON below the byte cap could raise a decoder RecursionError and drop the HTTP connection. A small nesting fixture did not exercise the actual runtime's limit. The wire regression must exceed the decoder's limit while staying below the byte cap and verify a controlled client error and server health afterward.

The review additionally noted narrow bundle diversity, tall compact sheets and inconsistent prevalidation limits. These are separate from claims that an output is technically well-formed.

## Release acceptance

Do not ship merely because the original suite passed. Require reproducing the failures, tests that fail before fixes and pass afterward, full-suite rerun, and a fresh independent verdict on the revised code. Final command output and verdict are recorded in the release verification artifact. No commit/push or public server deployment is part of this task.

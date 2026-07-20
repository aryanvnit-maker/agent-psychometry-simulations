# Submission Manifest — Licensing Boundary

This repository contains **two separately-licensed bodies of work**. This file is
the authoritative boundary between them. Where any per-file header, README, or
other notice conflicts with this manifest, **this manifest and the referenced
LICENSE files govern.**

## 1. The FLF Submission (openly licensed)

The epistemic-assessment layer authored for the **FLF Epistemic Case Study
Competition** (flf.org). The Future of Life Foundation, the competition judges,
and the public may freely use, run, reproduce, and publish these materials under
the licenses below.

**Code — MIT License** (see [`LICENSE-FLF-CODE`](LICENSE-FLF-CODE)):
- `src/evaluation/epistemic_schema.py`
- `src/scenarios/epistemic.py`
- `phases/phase_e/*.py`

**Documentation & result data — CC-BY-4.0** (see [`LICENSE-FLF-DOCS`](LICENSE-FLF-DOCS)):
- `docs/flf-submission.md`
- `docs/flf-submission-concise.md`
- `results/epistemic_maps/*.json`
- `results/phase_e.jsonl`, `results/phase_e_gemini31.jsonl`
- `results/phase3*.jsonl`, `results/transcripts/*` (cited run artifacts)

## 2. The Kalibr Engine (proprietary)

Everything else in this repository — the multi-agent psychometry engine and all
prior/parallel research. **All rights reserved** (see [`LICENSE`](LICENSE)). This
includes, without limitation:
- `src/` — all files **except** the two FLF files listed above
- `phases/` — all **except** `phase_e/`
- `kalibr/`, `judge0/`, `scripts/`, `reproduce.py`, and all other files

The Kalibr engine is **not** part of the FLF submission and is **not** covered by
any license grant made in connection with the FLF competition, except the narrow
reproduction-and-evaluation license stated in [`LICENSE`](LICENSE).

## Why the boundary matters

The FLF pipeline (`phases/phase_e/`) *imports* the Kalibr engine to run. The FLF
submission is therefore the epistemic layer that sits **on top of** the engine —
not the engine itself. Submitting the epistemic layer to the contest grants FLF
rights to that layer only; it does not place the engine in the public domain or
grant FLF general rights to it. `LICENSE` grants FLF exactly one thing with
respect to the engine: the right to run it in order to reproduce and verify this
submission.

## Note on prior versions

Portions of the Kalibr engine were previously published under AGPL-3.0. The
author, as sole copyright holder, elects the terms in `LICENSE` for the current
and future versions of those files. License grants already made for
previously-published versions are not retroactively revoked; they attach only to
those prior versions.

---

Copyright (c) 2026 Aryan Shah. Contact: aryan199841@gmail.com

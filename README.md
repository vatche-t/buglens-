---
title: BugLens
emoji: 🔍
colorFrom: gray
colorTo: yellow
sdk: gradio
sdk_version: 6.17.3
python_version: "3.12"
app_file: app.py
pinned: false
license: apache-2.0
short_description: Turn a bug screenshot into an honest, Jira-ready report.
tags:
  - build-small-hackathon
  - backyard-ai
  - tiny-titan
  - off-brand
  - minicpm-v
  - openbmb
  - modal
  - codex
---

# BugLens

BugLens turns a bug screenshot and a one-line tester note into a Jira-ready bug report, a missing-info checklist, regression tests, and edge-case notes — using a ~1.3B vision model that stays honest about what it cannot see.

**Build Small Hackathon** · Track: 🏡 Backyard AI · Model: [`openbmb/MiniCPM-V-4.6`](https://huggingface.co/openbmb/MiniCPM-V-4.6) (~1.3B)

- 🎥 Demo video: _coming soon_
- 📣 Social post: _coming soon_

## The idea

QA testers spend real time turning screenshots into structured tickets. BugLens does it in one read — and its differentiator is **honesty**: a small model that refuses to invent context it cannot perceive (browser, OS, device, user role, environment, backend state) and instead hands you a "confirm before filing" checklist.

## How it works (technical approach)

- **Frontend:** a custom React UI served via `gradio.Server` (FastAPI + Gradio's API engine) — deliberately beyond stock Gradio (**Off-Brand**).
- **Contract:** one validated Pydantic `BugReport` flows through the whole app and serializes to the exact JSON the UI renders into four cards.
- **Pipeline (two calls):** screenshot → factual UI observation (vision) → strict-JSON structuring → Pydantic validation → cards + Jira / GitHub / CSV exports.
- **Model:** `openbmb/MiniCPM-V-4.6` (~1.3B, SigLIP2-400M + Qwen3.5-0.8B) — image-native and strong at OCR / UI reading (**Tiny Titan**, **OpenBMB**).
- **Inference backend:** a Modal GPU endpoint the Space calls over HTTPS (**Modal**); a mock mode keeps the UI fully runnable during development.

## Run it locally

See [`UV.md`](UV.md) for details.

```bash
uv sync --extra dev
uv run pytest            # contract, render, and endpoint tests
uv run python app.py     # serves BugLens on http://localhost:7860
```

## Verified stack

- Python `>=3.11`, package manager: `uv`
- Gradio `6.17.3` · Pydantic `2.13.4` · Pillow `12.2.0` · Requests `2.34.2`
- Modal backend: Modal `1.4.3` + Transformers `5.10.2` (install with `av` instead of `torchcodec` to avoid CUDA conflicts)

## Plans

- [`01_research_verified_stack.md`](docs/plans/01_research_verified_stack.md)
- [`02_step_by_step_execution_plan.md`](docs/plans/02_step_by_step_execution_plan.md)
- [`03_architecture_flows.md`](docs/plans/03_architecture_flows.md)
- [`04_prompt_schema_quality_plan.md`](docs/plans/04_prompt_schema_quality_plan.md)
- [`05_submission_readme_demo_social.md`](docs/plans/05_submission_readme_demo_social.md)

## Contribution strategy

Codex contribution is part of the submission strategy. See [`docs/CONTRIBUTION_STRATEGY.md`](docs/CONTRIBUTION_STRATEGY.md).

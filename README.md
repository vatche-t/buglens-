# BugLens

BugLens turns a screenshot and a one-line tester note into a Jira-ready bug report, a missing-info checklist, regression tests, and edge-case notes.

This repository is currently in planning/scaffold mode. The detailed build plan lives in [`docs/plans`](docs/plans).

## Target

- Hugging Face Build Small Hackathon
- Track: Backyard AI
- Primary model: `openbmb/MiniCPM-V-4.6`
- Core differentiator: honest missing-info reporting instead of guessing unavailable context

## Verified Stack

- Python `>=3.11`
- Package manager: `uv`
- Gradio `6.17.3`
- Pydantic `2.13.4`
- Pillow `12.2.0`
- Requests `2.34.2`
- Optional Modal backend: Modal `1.4.3` + Transformers `5.10.2`

See [`UV.md`](UV.md) for setup and local commands.

## Planned App Flow

1. Upload screenshot.
2. Add tester note.
3. Generate factual UI observation.
4. Convert observation into validated bug artifact.
5. Render four cards:
   - Bug report
   - Missing info
   - Regression tests
   - Edge cases
6. Export Jira markdown, GitHub issue markdown, and CSV tests.

## Plans

- [`01_research_verified_stack.md`](docs/plans/01_research_verified_stack.md)
- [`02_step_by_step_execution_plan.md`](docs/plans/02_step_by_step_execution_plan.md)
- [`03_architecture_flows.md`](docs/plans/03_architecture_flows.md)
- [`04_prompt_schema_quality_plan.md`](docs/plans/04_prompt_schema_quality_plan.md)
- [`05_submission_readme_demo_social.md`](docs/plans/05_submission_readme_demo_social.md)

## Contribution Strategy

Codex contribution is part of the submission strategy. See [`docs/CONTRIBUTION_STRATEGY.md`](docs/CONTRIBUTION_STRATEGY.md).

# BugLens Plan 05 - Submission, README, Demo, And Social Pack

Research date: 2026-06-09

Purpose: make the final submission feel complete, honest, and easy for judges to evaluate.

## Final Submission Claims

Only claim what is true in the final build.

Recommended final claims:

- Track: Backyard AI.
- Sponsor: OpenBMB, because MiniCPM-V 4.6 is central.
- Special: Tiny Titan, because the model is genuinely tiny.
- Special: Best Demo, if video and social are polished.
- Badge: Off-Brand, if custom UI is clearly beyond stock Gradio.
- Badge: Field Notes, if a blog/report is published.
- Sponsor: OpenAI/Codex, if Codex-attributed commits are present.
- Sponsor: Modal, only if the live app uses Modal.

Do not claim:

- Off the Grid if inference uses Modal, HF APIs, or any cloud model endpoint.
- Llama Champion unless runtime is llama.cpp.
- Well-Tuned unless you publish and use a fine-tuned model.
- Best Agent unless the app truly performs agentic planning/action.

## README Frontmatter Starter

Use exact versions after final testing.

```yaml
---
title: BugLens
emoji: "🔍"
colorFrom: indigo
colorTo: orange
sdk: gradio
sdk_version: "6.17.3"
app_file: app.py
tags:
  - build-small-hackathon
  - backyard-ai
  - minicpm
  - openbmb
  - tiny-titan
  - off-brand
  - field-notes
  - best-demo
  - codex
---
```

Add `modal` only if Modal is actually used in production.

## README Structure

```text
# BugLens

One sentence:
BugLens turns a screenshot and a one-line tester note into a Jira-ready bug report, missing-info checklist, regression tests, and edge-case list.

## Why this exists
Specific QA/product pain.

## How it works
Screenshot -> factual observation -> schema-valid bug artifact -> four cards.

## The honest part
BugLens does not pretend to know browser, device, role, environment, or backend cause from a screenshot.

## Model and stack
MiniCPM-V 4.6, Gradio, Pydantic, optional Modal.

## Demo
Video link.

## Try it
Built-in examples and upload your own screenshot.

## Exports
Jira markdown, GitHub issue, CSV regression tests.

## Small-model fit
Why 1.2B-1.3B is enough for narrow screenshot QA.

## Limitations
What BugLens cannot infer.

## Field Notes
Link to blog/report.

## Credits and sources
Links to model card, Gradio docs, hackathon page.
```

## 60-Second Demo Script

Use this exact timing.

### 0-7 seconds: pain

Show a bug screenshot and say:

```text
Every QA team gets screenshots like this, then someone has to turn it into a real ticket by hand.
```

### 7-18 seconds: input

Upload screenshot, type:

```text
Deposit button does not respond after entering amount.
```

Say:

```text
BugLens takes the screenshot plus the tester note.
```

### 18-32 seconds: output

Click Generate. Show four cards.

Say:

```text
It creates a bug report, missing-info checklist, regression tests, and edge cases.
```

### 32-43 seconds: differentiator

Zoom into Missing Info.

Say:

```text
This is the important part. It does not guess the browser, device, user role, or backend cause. It asks the tester to confirm them.
```

### 43-53 seconds: usefulness

Click Jira export and CSV export.

Say:

```text
The output is ready for Jira and gives QA regression tests they can actually run.
```

### 53-60 seconds: small-model close

Say:

```text
It runs on MiniCPM-V 4.6, a tiny OpenBMB vision model. Small, honest, and useful.
```

End with Space URL on screen.

## Social Post Draft

Use after the demo is recorded.

```text
I built BugLens for the @huggingface Build Small Hackathon.

It turns a bug screenshot + one tester note into:
- a Jira-ready bug report
- missing info the AI refuses to guess
- regression tests
- edge cases

The best part: it runs on MiniCPM-V 4.6, a tiny OpenBMB vision model. The product idea is not "AI knows everything." It is "AI should be honest about what it cannot see."

Demo: [video link]
Space: [space link]

#BuildSmall #Gradio #MiniCPM #OpenBMB
```

If Modal is used, add:

```text
Inference is served through Modal GPU while the public app stays a Hugging Face Gradio Space.
```

If Codex was used, add:

```text
Built with OpenAI Codex helping scaffold the app, schema, tests, and deployment path.
```

## Field Notes Outline

Title:

```text
BugLens Field Notes: Teaching a Tiny Vision Model To Say "I Don't Know"
```

Sections:

1. The problem: screenshots are not bug reports.
2. Why small models fit this task.
3. The core design: two calls, one schema.
4. What went wrong at first: model guessed missing context.
5. Prompt fix: separate visible facts from inferred context.
6. The Missing Info card.
7. What MiniCPM-V 4.6 handled well.
8. What it still cannot know.
9. What I would build next.

Add images:

- Screenshot of BugLens input.
- Screenshot of four output cards.
- Screenshot zoomed on Missing Info.
- Optional before/after output comparison.

## Final Checklist

Before submitting:

- [ ] Space is in the official Build Small Hackathon org.
- [ ] Space opens in a logged-out browser.
- [ ] Four built-in examples work.
- [ ] Uploading a new screenshot works.
- [ ] Missing Info card never hallucinates browser/device/env.
- [ ] Jira markdown copies cleanly.
- [ ] CSV downloads cleanly.
- [ ] README has correct frontmatter.
- [ ] README links demo video.
- [ ] README links social post.
- [ ] README links Field Notes report if claiming Field Notes.
- [ ] README names MiniCPM-V 4.6 and links model card.
- [ ] README honestly says whether Modal is used.
- [ ] Requirements are pinned to tested versions.
- [ ] Codex-attributed commits exist if claiming Codex.
- [ ] No false claims: Off the Grid, Llama Champion, Well-Tuned, Best Agent.

## Source Links To Include

- Official hackathon page: https://huggingface.co/build-small-hackathon
- MiniCPM-V 4.6 model card: https://huggingface.co/openbmb/MiniCPM-V-4.6
- MiniCPM-V Transformers docs: https://huggingface.co/docs/transformers/main/model_doc/minicpmv4_6
- Gradio Server mode: https://www.gradio.app/guides/server-mode
- Gradio Server announcement: https://huggingface.co/blog/introducing-gradio-server
- ZeroGPU docs: https://huggingface.co/docs/hub/spaces-zerogpu
- Gradio with Modal guide: https://www.gradio.app/guides/deploying-gradio-with-modal
- Gradio PyPI: https://pypi.org/project/gradio/
- Transformers PyPI: https://pypi.org/project/transformers/
- Modal PyPI: https://pypi.org/project/modal/


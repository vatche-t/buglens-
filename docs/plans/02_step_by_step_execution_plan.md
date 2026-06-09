# BugLens Plan 02 - Step By Step Execution Plan

Research date: 2026-06-09

This is the build order from today to final submission. It assumes no code is written yet and focuses on what you should ask Codex to do each day.

## North Star

By June 15, 2026, submit a polished Gradio Space inside the official Build Small Hackathon org that turns bug screenshots into structured QA artifacts, with a strong demo, social post, Field Notes write-up, and evidence of Codex use.

The winning rule: deploy the ugly working Space first, then make it beautiful.

## Day 0 - Today, June 9

Goal: remove ambiguity and set up the public skeleton.

1. Confirm you are registered and inside the official Hugging Face org.
   - Org: https://huggingface.co/build-small-hackathon
   - If you are not registered/inside the org, solve this first. Registration is closed, so you must already be in.

2. Create the GitHub repo.
   - Suggested name: `buglens`
   - Keep it public if possible.
   - Add a short description: "Small-model QA assistant that turns screenshots into honest bug reports."

3. Open the repo in OpenAI Codex.
   - Ask Codex to scaffold only the clean project layout.
   - Make sure Codex-attributed commits appear in the repo history.
   - Do not let Codex build random features yet.

4. Create the Hugging Face Space.
   - Space name: `BugLens` or `buglens`
   - SDK: Gradio.
   - Hardware: CPU basic at first.
   - Organization: official Build Small Hackathon org.

5. Deploy a fake-output skeleton.
   - Upload a screenshot.
   - Enter a short note.
   - Click Generate.
   - Four cards render using hardcoded data.
   - This is ugly but public.

Definition of done:

- GitHub repo exists.
- HF Space exists under the official org.
- App boots.
- Four output cards are visible.
- Codex has at least one meaningful attributed commit.

## Day 1 - June 10: Vision Read

Goal: screenshot -> factual UI observation.

1. Test MiniCPM-V 4.6 manually using the official model card examples.
   - Model card: https://huggingface.co/openbmb/MiniCPM-V-4.6
   - Use one real app screenshot.

2. Implement the first model call.
   - Input: screenshot + optional user note.
   - Output: factual observation text.
   - The prompt must ban guessing.

3. Build three demo screenshots.
   - `broken_payment.png`
   - `login_error.png`
   - `mobile_overflow.png`

4. Save the raw observation output for each example.
   - These become few-shot examples and Field Notes material.

Definition of done:

- BugLens reads a screenshot and returns visible UI facts.
- It explicitly says when browser/device/environment are unknown.
- At least three example screenshots are in the Space.

## Day 2 - June 11: Structuring Contract

Goal: factual observation -> schema-valid bug artifact.

1. Define the output contract before prompting more.
   - Title.
   - Severity: `P1`, `P2`, or `P3`.
   - Component.
   - Steps.
   - Expected.
   - Actual.
   - Missing info.
   - Regression tests.
   - Edge cases.

2. Ask Codex to implement the Pydantic schema.
   - Use `pydantic==2.13.4`.
   - No loose dict contract.
   - Invalid JSON should not crash the app.

3. Implement call 2.
   - Input: observation + user note.
   - Output: strict JSON.
   - Validate with Pydantic.
   - Retry once if the output is not valid JSON.

4. Render the four cards from validated data.
   - No hardcoded fake outputs after this point.

Definition of done:

- Real screenshot generates the four cards.
- Missing-info card is never empty unless all context is genuinely known.
- Invalid model output gets a clear retry/error state.

## Day 3 - June 12: Modal Decision Gate

Goal: decide whether to chase Modal or lock the core app.

Morning:

1. Stand up a Modal endpoint for MiniCPM-V 4.6.
   - Modal package: `modal==1.4.3`
   - Transformers package: `transformers[torch]==5.10.2`
   - Model: `openbmb/MiniCPM-V-4.6`

2. Keep Hugging Face Space as the frontend.
   - The Space calls the Modal endpoint over HTTPS.
   - Do not serve the whole Gradio app through Modal unless necessary.

Afternoon decision:

- If Modal is stable: keep it and claim Modal-powered architecture.
- If Modal is not stable: switch to ZeroGPU or simpler hosted path and drop the Modal prize.

Hard rule:

- Do not lose the whole hackathon trying to win Modal. Modal is a bonus. A finished BugLens beats a half-working Modal experiment.

Definition of done:

- Either Modal endpoint works and is wired, or the fallback path is chosen.
- README honestly describes whichever path is real.

## Day 4 - June 13: Polish And Exports

Goal: make the app look intentional and useful.

1. Upgrade the UI for Off-Brand.
   - Preferred: `gradio.Server` custom frontend.
   - Fast fallback: Gradio Blocks with custom HTML/CSS cards.

2. Add exports.
   - Jira markdown.
   - GitHub issue markdown.
   - CSV for regression tests.

3. Add examples.
   - Four built-in screenshots.
   - Each example should show a different bug category:
     - Broken payment/deposit.
     - Login error.
     - Empty dashboard.
     - Mobile layout overflow.

4. Add tests.
   - Schema validation test.
   - Render/export formatting test.
   - Prompt fixture test if time allows.

5. Add Field Notes draft.
   - What problem you solved.
   - Why small model is enough.
   - What the model cannot know.
   - Failure modes and mitigation.

Definition of done:

- App no longer looks like stock Gradio.
- Exports work.
- Examples are clickable.
- Tests pass.
- Field Notes draft exists.

## Day 5 - June 14: Demo, Social, README

Goal: package the story.

1. Record the 60-second demo.
   - Show the pain.
   - Upload screenshot.
   - Generate cards.
   - Zoom on Missing Info.
   - Export Jira markdown/CSV.
   - End with "1.3B model, honest by design."

2. Publish social post.
   - Use X or LinkedIn.
   - Include a short clip or screenshot.
   - Tag relevant accounts if comfortable:
     - `@huggingface`
     - `@Gradio`
     - `@OpenBMB`
     - `@OpenAI`
     - `@modal_labs` if Modal is used.

3. Finish README.
   - Include track.
   - Include targeted awards/badges.
   - Include demo video link.
   - Include social post link.
   - Include model and param story.
   - Include honest limitation section.

4. Freeze versions.
   - Replace version ranges with exact versions tested.
   - Confirm Space rebuilds from a clean state.

Definition of done:

- Video link is live.
- Social post is live.
- README is submission-ready.
- Space works after rebuild.

## Day 6 - June 15 Morning: Submit

Goal: final checks and submit before deadline pressure.

1. Open Space in a fresh browser.
2. Run all four built-in examples.
3. Upload one fresh screenshot.
4. Copy Jira markdown.
5. Download CSV.
6. Verify README links.
7. Verify source links.
8. Verify no false badge claims.
9. Submit Space link, demo video, and social post.

Definition of done:

- Submission is complete before the final hours.

## Codex Prompts To Use In Order

Use these as high-level prompts to OpenAI Codex, one at a time:

1. "Scaffold a clean Gradio app for BugLens with separate modules for schema, prompts, model calls, rendering, and tests. Do not implement model inference yet. Keep app.py thin."
2. "Implement the Pydantic output schema and renderer functions for Jira markdown, GitHub issue markdown, CSV test cases, and four UI card payloads."
3. "Implement the screenshot observation function using MiniCPM-V 4.6. The prompt must describe only visible UI facts and must not infer browser, OS, device, role, environment, or backend cause."
4. "Implement the structuring function that converts observation text into strict JSON matching the schema, validates with Pydantic, retries once on invalid JSON, and returns a graceful error state."
5. "Upgrade the UI to a custom BugLens interface that clearly differs from stock Gradio, preserves the four-card workflow, and works on mobile."
6. "Add focused tests for schema validation, export formatting, invalid JSON fallback, and missing-info behavior."
7. "Write the final README with hackathon frontmatter, model choices, small-model justification, demo/social links, and honest limitations."


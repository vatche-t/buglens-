# Field Notes — Building BugLens

_Build Small Hackathon · Backyard AI · `openbmb/MiniCPM-V-4.6` (~1.3B)_

> Working notes on what we built, why a tiny vision model is the right tool for
> it, where it falls short, and the engineering calls we made along the way.

## The problem

QA testers and PMs spend a surprising amount of time turning a bug **screenshot**
into a usable **ticket**: a title, severity, repro steps, expected vs actual, the
tests to add, and — crucially — the list of things someone still needs to check.
It's repetitive, and the hard part isn't writing prose, it's being *disciplined*:
not asserting things you can't actually see, and not forgetting the boring
follow-up questions.

That shape — narrow task, visual input, structured output, discipline over
creativity — is a great fit for a small model.

## The approach: an honest small model

BugLens turns one screenshot (+ an optional one-line tester note) into four cards:

1. **Bug report** — title, severity, summary, steps, expected/actual, environment.
2. **Missing info** — the differentiator: what the model *cannot* determine from a
   static image, phrased as questions to confirm before filing.
3. **Regression tests** — Given/When/Then, QA-runnable.
4. **Edge cases** — practical risks worth checking.

The product thesis is **honesty**. A screenshot only shows the surface, so BugLens
is built to refuse to guess browser, OS, device, viewport, user role, environment,
backend state, or network status. Instead of hallucinating those, it lists them as
unconfirmed and tells you why each one matters.

### Two-call pipeline

We split inference into two deliberate calls:

- **Call 1 — perception.** "Describe only what is visible." The prompt explicitly
  bans inferring causes or unobservable context. Output is plain factual bullets.
- **Call 2 — structuring.** Turn that observation into strict JSON matching a fixed
  schema, validated with Pydantic, with **one repair retry** if the JSON is invalid.

Separating perception from product-reasoning made the model noticeably more honest
(the "what I can't see" list is generated against the *observation*, not the raw
image) and made debugging far easier — you can read exactly what the model claimed
to see before it ever shaped a ticket.

## Why a ~1.3B model is enough here

MiniCPM-V 4.6 is ~1.3B parameters (SigLIP2-400M vision encoder + a Qwen3.5-0.8B
backbone). For BugLens that's not a compromise, it's a fit:

- The task is mostly **OCR + UI perception** (read the error text, see that a button
  is greyed out), which small vision models do well.
- The "intelligence" lives in the **schema and the prompt discipline**, not in open-
  ended reasoning. A validated contract does the heavy lifting a bigger model would
  otherwise be asked to improvise.
- Small means cheap and fast enough to serve on modest GPU, which keeps the whole
  thing deployable and demo-able.

The narrow scope is what makes the small model honest *and* sufficient: it does one
useful thing and admits what it doesn't know.

## Where small models struggle (and what we did about it)

- **Strict JSON.** Small models drift from a complex schema. Mitigation: a fixed
  field-name schema in the prompt, defensive parsing (strip code fences / prose),
  Pydantic validation, and a single repair retry; on a second failure we surface the
  raw observation instead of pretending we have a report.
- **Severity calibration.** It's tempting to call everything P1/critical when the
  error text "looks dramatic." We pinned severity rules (tie it to visible/stated
  impact) into the prompt.
- **Over-claiming.** The default failure mode of any VLM is to invent plausible
  context. The entire missing-info design exists to convert that temptation into an
  explicit, useful checklist.
- **Tiny text / dense dashboards.** Downsampling trades detail for speed; we default
  to `downsample_mode="16x"` and reserve `4x` for OCR-heavy screenshots.

## Engineering decisions

- **Custom frontend on `gradio.Server` (Off-Brand).** `gradio.Server` is a FastAPI
  subclass with Gradio's API engine, so we serve a bespoke React UI at `/` and the
  jsx assets under `/static`, keeping queue/streaming/Spaces hosting. (Gotcha: a
  static mount at `/` shadows Gradio's own `/gradio_api/*` routes and breaks launch —
  mount assets under a prefix.)
- **One canonical contract.** A single Pydantic `BugReport` flows through the whole
  app and serializes — via field aliases — to the exact JSON the UI already rendered.
  Backend and frontend speak one language.
- **Modal for inference.** A GPU container loads the model once (`@modal.enter`) and
  serves a POST endpoint; the lightweight Space calls it over HTTPS. Install with
  `av` instead of `torchcodec` to dodge a CUDA-version conflict noted on the model
  card.
- **Mock mode.** Built-in examples return canned validated reports so the app is
  fully explorable (and the UI buildable) without a GPU; flipping `BUGLENS_BACKEND`
  swaps in real inference.
- **Client-side exports.** Copy-Jira / Copy-GitHub / Download-CSV format from the
  report payload already in the browser, so they work for live uploads too.

## On honesty, again

The most important UI element is the one that says _"I can't see this."_ We even
removed a fake "Sent to Jira — JIRA-4821 created" toast from the prototype: if the
product's whole pitch is not pretending, the demo shouldn't pretend either. The
export button copies markdown and says so.

## Working with Codex

Development ran as small, single-concern PRs (schema, render, app, vision,
structuring, Modal, UI wiring), each reviewed and merged through OpenAI Codex.
Codex caught two real bugs we'd have shipped: a stale-fetch race that could
overwrite a newer result, and an object-URL cleanup path that leaked on failed
uploads. Keeping the history granular made those reviews tractable.

## Artifacts to capture for the writeup

_(fill in during the demo pass)_

- [ ] Before: a screenshot where an earlier prompt hallucinated environment/browser.
- [ ] After: the improved missing-info card on the same input.
- [ ] A short before/after table of prompt changes and their effect.
- [ ] One real uploaded screenshot end-to-end on the live Modal backend.

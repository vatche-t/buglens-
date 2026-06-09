# BugLens Plan 03 - Architecture, Flows, And Product Shape

Research date: 2026-06-09

Purpose: define the system shape before implementation so the app feels engineered, not improvised.

## Product Flow

```mermaid
flowchart TD
    A["Tester uploads screenshot"] --> B["Tester adds one-line note"]
    B --> C["BugLens reads visible UI facts"]
    C --> D["BugLens structures validated bug artifact"]
    D --> E["Bug report card"]
    D --> F["Missing info card"]
    D --> G["Regression tests card"]
    D --> H["Edge cases card"]
    E --> I["Export Jira markdown"]
    G --> J["Export CSV"]
    E --> K["Export GitHub issue"]
```

## Primary Technical Architecture

This is the recommended plan if Modal works by the Thursday gate.

```mermaid
flowchart LR
    U["User in browser"] --> S["Hugging Face Gradio Space"]
    S --> V["Validate image and note"]
    V --> M["Modal GPU endpoint"]
    M --> MV["MiniCPM-V 4.6"]
    MV --> O["Factual observation"]
    O --> M2["Structuring call"]
    M2 --> J["Strict JSON"]
    J --> P["Pydantic validation"]
    P --> R["Render cards and exports"]
    R --> U
```

Why this architecture:

- Meets the requirement that the app is a Gradio Space.
- Keeps the public app simple.
- Uses Modal enough to honestly qualify as Modal-powered.
- Lets the GPU model stay outside the frontend runtime.
- Reduces Gradio sticky-session risk because the Space remains the user-facing app.

## Fallback Technical Architecture

Use this if Modal is unstable.

```mermaid
flowchart LR
    U["User in browser"] --> S["Hugging Face Gradio Space"]
    S --> Z["ZeroGPU decorated function"]
    Z --> MV["MiniCPM-V 4.6"]
    MV --> O["Observation and structured JSON"]
    O --> P["Pydantic validation"]
    P --> R["Four cards and exports"]
    R --> U
```

Important ZeroGPU facts:

- Source: https://huggingface.co/docs/hub/spaces-zerogpu
- Use `@spaces.GPU` around GPU-dependent functions.
- ZeroGPU is compatible with Gradio SDK only.
- Personal hosting requires PRO; organization hosting requires Team/Enterprise.
- Daily quotas and queue priority matter.

## Optional Local-First Architecture

Only build this after the core submission works.

```mermaid
flowchart LR
    U["User"] --> L["Local BugLens runtime"]
    L --> LC["llama.cpp or Ollama"]
    LC --> G["MiniCPM-V 4.6 GGUF"]
    G --> O["Observation"]
    O --> P["Pydantic validation"]
    P --> R["Cards and exports"]
```

Why this matters:

- Needed for a credible Off the Grid claim.
- Needed for a credible Llama Champion claim if using llama.cpp.
- Not needed for the core win.
- Risky to prioritize before the Space is done.

## Two-Call Model Pipeline

```mermaid
sequenceDiagram
    participant UI as Gradio UI
    participant V as Vision Call
    participant S as Structuring Call
    participant P as Pydantic
    participant R as Renderer

    UI->>V: screenshot + tester note + factual prompt
    V-->>UI: visible UI observation only
    UI->>S: observation + tester note + JSON schema prompt
    S-->>UI: JSON candidate
    UI->>P: validate JSON
    alt valid
        P-->>R: BugReport object
        R-->>UI: cards, Jira markdown, GitHub markdown, CSV
    else invalid
        P-->>S: retry once with strict JSON reminder
        S-->>P: second JSON candidate
        P-->>UI: valid output or graceful error card
    end
```

Why two calls:

- Call 1 is perception: "What is visible?"
- Call 2 is product reasoning: "How should a bug ticket be shaped?"
- Separating the calls improves honesty, makes debugging easier, and gives you a clean demo explanation.

## Data Contract

Use one validated object as the app contract:

```text
BugReport
- title: string
- severity: enum[P1, P2, P3]
- component: string
- steps: list[string]
- expected: string
- actual: string
- missing_info: list[string]
- regression_tests: list[RegressionTest]
- edge_cases: list[string]

RegressionTest
- id: string
- desc: string
```

Do not allow UI code, export code, and model code to each invent their own shape. Everything should pass through this contract.

## Module Layout

```text
buglens/
  app.py
  requirements.txt
  README.md
  buglens/
    __init__.py
    schema.py
    prompts.py
    vision.py
    structure.py
    render.py
    examples.py
  modal_app.py
  theme.py
  examples/
    broken_payment.png
    login_error.png
    empty_dashboard.png
    mobile_overflow.png
  tests/
    test_schema.py
    test_render.py
    test_missing_info.py
```

Responsibilities:

| File | Responsibility |
|---|---|
| `app.py` | Build UI and wire events only |
| `schema.py` | Pydantic contract |
| `prompts.py` | Versioned prompts |
| `vision.py` | Screenshot to observation |
| `structure.py` | Observation to validated report |
| `render.py` | Jira, GitHub, CSV, card formatting |
| `modal_app.py` | Modal GPU endpoint |
| `theme.py` | UI theme and Off-Brand styling |
| `tests/` | Contract and rendering tests |

## UI Layout

```mermaid
flowchart TD
    A["Header: BugLens"] --> B["Left panel: upload screenshot, note, examples"]
    A --> C["Right panel: Generate button and status"]
    C --> D["Bug Report card"]
    C --> E["Missing Info card"]
    C --> F["Regression Tests card"]
    C --> G["Edge Cases card"]
    D --> H["Copy Jira"]
    D --> I["Copy GitHub Issue"]
    F --> J["Download CSV"]
```

Design requirements:

- The first viewport should be the actual tool, not a landing page.
- The four cards are the product.
- Missing Info must be visually prominent.
- Export buttons should be obvious and useful.
- Use example screenshots so judges can try it immediately.
- Avoid huge hero copy. This is an operational QA tool.

## Reliability Requirements

Must handle:

- No screenshot uploaded.
- Huge screenshot.
- Unsupported file type.
- Empty user note.
- Model timeout.
- Invalid JSON.
- Missing fields.
- Model guesses context it should not guess.

Graceful states:

- "I need a screenshot to inspect the UI."
- "The model returned invalid JSON. Try again or use the observation text."
- "I cannot determine browser, device, user role, or environment from the screenshot."

## Performance Targets

Acceptable for hackathon:

- First cold generation: under 60 seconds.
- Warm generation: under 20 seconds.
- UI response after validation: immediate.
- Exports: instant.

If slow:

- Use MiniCPM `downsample_mode="16x"` first.
- Switch to `4x` only for tiny text/OCR-heavy screenshots.
- Limit max tokens for observation and structure calls.
- Use short example screenshots.


# BugLens Plan 01 - Verified Research And Tech Stack

Research date: 2026-06-09

Purpose: lock the correct hackathon rules, prize strategy, model choice, and current library versions before any code is written.

## Executive Decision

Build BugLens as a Hugging Face Gradio Space for the Backyard AI track. Use `openbmb/MiniCPM-V-4.6` as the primary model because it is a sponsor model, tiny enough for the Tiny Titan award, strong at UI/OCR screenshots, and aligned with the "honest small model" story.

The app should convert a screenshot plus a short tester note into four structured outputs:

1. Jira-ready bug report.
2. Missing-info checklist.
3. Regression test cases.
4. Edge cases and risk list.

The killer differentiator is the missing-info card. BugLens should never invent browser, OS, device, user role, environment, or backend state from an image. It should say what it cannot know.

## Correct Prize Map

Verified from the official Build Small Hackathon page:

Source: https://huggingface.co/build-small-hackathon

Core requirements:

- Every model must be `<= 32B` parameters.
- App must be built on Gradio.
- App must be hosted as a Hugging Face Space.
- Submission needs a short demo video.
- Submission needs a social-media post.
- Hack window: June 5-15, 2026.
- Submission close date: June 15, 2026.

Main target:

- Backyard AI track.
- Judged on specific real problem, real user use, honest fit with small-model constraint, and polish of the Gradio app.

Sponsor and special targets:

| Target | Why BugLens fits | Priority |
|---|---|---|
| Backyard AI placement | Real QA/product pain, direct practical use | Must-have |
| OpenBMB Awards | Core model is MiniCPM-V 4.6 | Must-have |
| Tiny Titan | MiniCPM-V 4.6 is built from SigLIP2-400M + Qwen3.5-0.8B, effectively around 1.2B-1.3B | Must-have |
| Off-Brand | Custom UI past default Gradio, ideally with `gradio.Server` or strong HTML/CSS cards | High |
| Best Demo | Strong demo video and social post | High |
| Field Notes | Blog/report about what was built and learned | High |
| Best Use of Codex | Develop through OpenAI Codex and preserve attributed commits | High |
| Modal Awards | Modal GPU endpoint or Modal-powered inference path | Medium |
| Bonus Quest Champion | Stack as many valid badges/awards as possible | Medium |

Do not falsely claim:

- Best Agent, unless you truly add agentic planning/tool execution. BugLens is a pipeline by default.
- Off the Grid if the final app depends on Modal, hosted APIs, or cloud inference.
- Llama Champion unless the final model runtime actually uses llama.cpp.
- Well-Tuned unless you publish and use a fine-tuned model on Hugging Face.
- Sharing is Caring unless you publish a useful trace/dataset on the Hub.

## Badge Strategy

Verified merit badges on the official page:

- Off the Grid: no cloud APIs; whole thing runs on the model in front of you.
- Well-Tuned: app uses a fine-tuned model published on Hugging Face.
- Off-Brand: custom frontend beyond default Gradio; official hint says `gr.Server`.
- Llama Champion: model runs through llama.cpp.
- Sharing is Caring: shared agent trace on the Hub.
- Field Notes: blog post or report about what was built and learned.

Recommended claim set for the realistic plan:

- Off-Brand.
- Field Notes.
- Possibly Sharing is Caring if you publish anonymized BugLens prompt/outputs as a dataset.

Recommended special-award claim set:

- Tiny Titan.
- Best Demo.
- OpenBMB.
- Best Use of Codex.
- Modal only if it is stable by the Thursday decision gate.

## Model Selection

Primary model:

- Model: `openbmb/MiniCPM-V-4.6`
- URL: https://huggingface.co/openbmb/MiniCPM-V-4.6
- License: Apache-2.0
- Task: image-text-to-text
- Official install note: `pip install "transformers[torch]>=5.7.0" torchvision torchcodec`
- Architecture noted by Hugging Face docs: SigLIP vision encoder plus Qwen3.5 language model backbone.
- Model card states it is based on SigLIP2-400M and Qwen3.5-0.8B.
- Model card says it supports image, multi-image, video understanding, OCR-like UI reading, vLLM, SGLang, llama.cpp, Ollama, BNB, AWQ, GPTQ, and GGUF variants.

Why this is the right model:

- It directly targets OpenBMB sponsor awards.
- It is small enough for Tiny Titan.
- It is image-native, so screenshots are a natural task.
- The small size strengthens the story: "BugLens does one narrow useful thing, and admits uncertainty."
- It avoids the temptation to use a larger 7B+ VLM for a task that mostly needs OCR, UI perception, and schema discipline.

Optional model/runtime variants:

| Use case | Option | When to use |
|---|---|---|
| Hosted GPU backend | Transformers on Modal | Best for speed and Modal award |
| HF Space fallback | ZeroGPU with `@spaces.GPU` | If Modal blocks progress |
| Local-first demo | GGUF / llama.cpp variant | If chasing Off the Grid and Llama Champion |
| Harder reasoning | MiniCPM-V-4.6-Thinking | Only if screenshots need more reasoning and latency is acceptable |

## Current Library Versions

Pin exact versions before final submission. Current verified versions from PyPI and official docs:

| Package | Current verified version / constraint | Source |
|---|---:|---|
| `gradio` | `6.17.3`, uploaded Jun 7, 2026 | https://pypi.org/project/gradio/ |
| `transformers` | `5.10.2`, uploaded Jun 4, 2026 | https://pypi.org/project/transformers/ |
| `modal` | `1.4.3`, released May 18, 2026 | https://pypi.org/project/modal/ |
| `pillow` | `12.2.0`, released Apr 1, 2026 | https://pypi.org/project/pillow/ |
| `requests` | `2.34.2`, released May 14, 2026 | https://pypi.org/project/requests/ |
| `pydantic` | stable: `2.13.4`; latest visible is pre-release `2.14.0a1` | https://pypi.org/project/pydantic/ |

Recommended pins for the final Space:

```text
gradio==6.17.3
pydantic==2.13.4
pillow==12.2.0
requests==2.34.2
```

Recommended pins for the Modal backend:

```text
modal==1.4.3
transformers[torch]==5.10.2
torchvision
torchcodec
pillow==12.2.0
accelerate
```

Important note from the MiniCPM model card:

- `torchcodec` can have CUDA compatibility issues.
- If this happens, replace `torchcodec` with `av`, or pin torch to the CUDA runtime used by the environment.

## Gradio And ZeroGPU Facts

Sources:

- Gradio Server mode guide: https://www.gradio.app/guides/server-mode
- Gradio Server announcement: https://huggingface.co/blog/introducing-gradio-server
- ZeroGPU docs: https://huggingface.co/docs/hub/spaces-zerogpu

Key facts:

- `gradio.Server` allows a fully custom frontend while keeping Gradio backend features.
- Server mode keeps API, queuing, streaming, MCP support, ZeroGPU support, and Spaces hosting.
- ZeroGPU is Gradio-only.
- ZeroGPU uses `@spaces.GPU` to allocate and release GPU for decorated functions.
- ZeroGPU hosting requires PRO for personal accounts, or Team/Enterprise for organizations.
- ZeroGPU supports Gradio 4+ and PyTorch 2.8+ to latest.
- Current ZeroGPU backing hardware is NVIDIA RTX Pro 6000 Blackwell, with 48GB default large and 96GB xlarge.

Recommended UI path:

- Use `gradio.Server` if time allows. It is the strongest Off-Brand signal.
- If time is tight, use Gradio Blocks plus custom HTML/CSS cards. Still visibly avoid stock UI.

## Modal Facts

Sources:

- Modal partner info on official hackathon page: https://huggingface.co/build-small-hackathon
- Gradio with Modal guide: https://www.gradio.app/guides/deploying-gradio-with-modal

Key facts:

- Modal is a hackathon sponsor.
- Official page lists $20,000 in Modal credits for top Modal-powered apps.
- The Gradio Modal guide suggests `max_containers=1` for Gradio sticky-session needs if serving Gradio through Modal.
- The guide also explicitly says GPU compute can be deployed in a separate Modal function and called from the Gradio app.

Recommended Modal path:

- Keep Hugging Face Space as the public submission front door.
- Put MiniCPM inference in a Modal GPU web endpoint.
- Have the Space call Modal for inference.
- This avoids serving the whole Gradio session through Modal, reducing sticky-session risk.

## Final Technical Decision

Primary build:

- HF Space: Gradio 6.17.3, Python 3.12 if available, CPU-basic frontend.
- Backend: Modal GPU endpoint running MiniCPM-V 4.6 through Transformers 5.10.2.
- App contract: Pydantic 2.13.4 schema.
- Model flow: screenshot + note -> factual observation -> structured JSON -> four cards and exports.

Fallback:

- If Modal is not stable by end of Thursday, switch to HF ZeroGPU or a hosted test path and drop the Modal award.

Optional stretch:

- Add a llama.cpp/GGUF local mode only if core app is already done. This is needed for Llama Champion/Off the Grid claims.


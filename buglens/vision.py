"""Call 1 of the pipeline: screenshot -> factual UI observation.

`transformers` is imported lazily inside `load_model`, so this module stays
importable on the lightweight Gradio frontend (which has no ML deps); the model
itself is loaded and run on the Modal GPU backend. `observe()` takes the model
and processor as arguments so the orchestration is testable without downloading
the ~1.3B model.
"""

from __future__ import annotations

from typing import Any

from buglens.config import DEFAULT_MODEL_ID
from buglens.prompts import vision_user_text

DEFAULT_DOWNSAMPLE = "16x"  # "4x" only for tiny OCR-heavy text (slower)
DEFAULT_MAX_NEW_TOKENS = 512
DEFAULT_MAX_SLICE_NUMS = 36  # handles high-resolution screenshots


def build_vision_messages(image: Any, note: str | None = None) -> list[dict]:
    """Build the chat messages for the vision call.

    `image` may be a PIL.Image (an uploaded screenshot) or a URL/path string.
    """

    if isinstance(image, str):
        image_part = {"type": "image", "url": image}
    else:
        image_part = {"type": "image", "image": image}
    return [
        {
            "role": "user",
            "content": [image_part, {"type": "text", "text": vision_user_text(note)}],
        }
    ]


def observe(
    model: Any,
    processor: Any,
    image: Any,
    note: str | None = None,
    *,
    downsample_mode: str = DEFAULT_DOWNSAMPLE,
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
    max_slice_nums: int = DEFAULT_MAX_SLICE_NUMS,
) -> str:
    """Run MiniCPM-V 4.6 to produce a factual observation of the screenshot.

    `downsample_mode` must be passed to both `apply_chat_template` and `generate`
    per the model card.
    """

    messages = build_vision_messages(image, note)
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
        downsample_mode=downsample_mode,
        max_slice_nums=max_slice_nums,
    ).to(model.device)
    generated = model.generate(
        **inputs,
        downsample_mode=downsample_mode,
        max_new_tokens=max_new_tokens,
    )
    prompt_len = inputs["input_ids"].shape[-1]
    text = processor.decode(generated[0][prompt_len:], skip_special_tokens=True)
    return text.strip()


def load_model(model_id: str = DEFAULT_MODEL_ID):
    """Load MiniCPM-V 4.6 and its processor (imports transformers lazily).

    Install with ``transformers[torch]>=5.7.0 torchvision av`` — ``av`` instead
    of ``torchcodec`` avoids the CUDA-version conflict noted on the model card.
    Called by the Modal GPU backend, not by the CPU frontend.
    """

    from transformers import AutoModelForImageTextToText, AutoProcessor  # noqa: PLC0415

    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForImageTextToText.from_pretrained(
        model_id, torch_dtype="auto", device_map="auto"
    )
    return model, processor

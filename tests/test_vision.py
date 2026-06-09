"""Tests for the vision call orchestration (no real model download)."""

from buglens import vision
from buglens.prompts import VISION_PROMPT, vision_user_text


def test_vision_user_text_includes_prompt_and_note() -> None:
    text = vision_user_text("Pay button does nothing")
    assert VISION_PROMPT in text
    assert text.endswith("Tester note: Pay button does nothing")


def test_vision_user_text_handles_missing_note() -> None:
    assert vision_user_text(None).endswith("Tester note: (none provided)")
    assert vision_user_text("   ").endswith("Tester note: (none provided)")


def test_build_messages_url_vs_image() -> None:
    url_msg = vision.build_vision_messages("https://x/y.png", "note")
    assert url_msg[0]["content"][0] == {"type": "image", "url": "https://x/y.png"}

    sentinel = object()  # stands in for a PIL.Image
    img_msg = vision.build_vision_messages(sentinel)
    assert img_msg[0]["content"][0] == {"type": "image", "image": sentinel}
    # The instruction text always bans guessing.
    assert "Do not guess browser" in img_msg[0]["content"][1]["text"]


class _FakeTensor:
    def __init__(self, length: int) -> None:
        self.shape = (1, length)


class _FakeInputs(dict):
    def to(self, _device):
        return self


class _FakeProcessor:
    def apply_chat_template(self, messages, **kwargs):
        self.template_kwargs = kwargs
        self.messages = messages
        return _FakeInputs(input_ids=_FakeTensor(3))

    def decode(self, ids, **kwargs):
        self.decoded_ids = ids
        return "  Visible facts:\n- A disabled Pay button  "


class _FakeModel:
    device = "cpu"

    def generate(self, **kwargs):
        self.generate_kwargs = kwargs
        return [[10, 11, 12, 13, 14, 15]]


def test_observe_passes_params_and_strips_output() -> None:
    model, processor = _FakeModel(), _FakeProcessor()

    out = vision.observe(model, processor, "shot.png", "note", downsample_mode="16x")

    assert out == "Visible facts:\n- A disabled Pay button"
    # downsample_mode + slice nums reach the template; downsample + tokens reach generate.
    assert processor.template_kwargs["downsample_mode"] == "16x"
    assert processor.template_kwargs["max_slice_nums"] == 36
    assert model.generate_kwargs["downsample_mode"] == "16x"
    assert model.generate_kwargs["max_new_tokens"] == 512
    # Only the newly generated tokens (after the prompt length of 3) are decoded.
    assert processor.decoded_ids == [13, 14, 15]

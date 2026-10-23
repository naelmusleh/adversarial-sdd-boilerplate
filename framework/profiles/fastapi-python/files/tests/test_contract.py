import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from main import GalleryItemV1, is_visible_in_collection  # noqa: E402


VALID = {
    "schema_version": "1",
    "item_id": "sample-item-0001",
    "content_type": "image/jpeg",
    "byte_size": 2048,
    "state": "active",
}


def test_accepts_valid_sample_and_preserves_id() -> None:
    assert GalleryItemV1.model_validate(VALID).item_id == "sample-item-0001"


@pytest.mark.parametrize(
    "payload",
    [
        {key: value for key, value in VALID.items() if key != "item_id"},
        {**VALID, "byte_size": 0},
        {**VALID, "schema_version": "2"},
    ],
)
def test_rejects_invalid_or_unsupported_major(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        GalleryItemV1.model_validate(payload)


def test_ignores_unknown_optional_and_hides_removed_items() -> None:
    item = GalleryItemV1.model_validate({**VALID, "optional_future": True})
    removed = GalleryItemV1.model_validate({**VALID, "state": "remove_requested"})
    assert item.item_id == "sample-item-0001"
    assert is_visible_in_collection(removed) is False

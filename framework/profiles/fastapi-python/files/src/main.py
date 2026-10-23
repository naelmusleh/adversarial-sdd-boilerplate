from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field


class GalleryItemV1(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    schema_version: Literal["1"]
    item_id: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    byte_size: int = Field(gt=0)
    state: Literal["active", "remove_requested"]


def is_visible_in_collection(item: GalleryItemV1) -> bool:
    return item.state == "active"


app = FastAPI(title="Synthetic FW-013 profile fixture")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "synthetic-fixture-only"}

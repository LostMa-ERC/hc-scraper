from bs4 import Tag
from dataclasses import dataclass

from pydantic import BaseModel, Field, field_validator

TRADITION_STATUS = ["fragmentary", "lost", "surviving", "unknown"]


@dataclass
class PartialWork:
    id: int
    title: str
    url: str

    @classmethod
    def from_list_item(cls, li: Tag) -> "PartialWork":
        title = li.find("a").get_text().strip()
        id_string = li.get("id").removeprefix("id")
        id = int(id_string)
        url = f"https://handschriftencensus.de/werke/{id_string}"
        return PartialWork(id=id, title=title, url=url)


class WorkModel(BaseModel):
    id: int
    title: str
    references: list[str | None] = Field(
        default=[], serialization_alias="described_at_URL"
    )
    status: str | None = Field(
        default="unknown", serialization_alias="tradition_status"
    )

    @field_validator("status")
    def validate_status(cls, value: str | None):
        if value:
            assert value in TRADITION_STATUS
            return value
        else:
            raise ValueError(
                f"{value} must be 1 of the following: {', '.join(TRADITION_STATUS)}"
            )

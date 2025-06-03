from bs4 import Tag
from dataclasses import dataclass

from pydantic import BaseModel, Field, field_validator

TRADITION_STATUS = ["fragmentary", "lost", "surviving", "unknown"]


@dataclass
class WorkNotice:
    id: int
    title: str
    url: str

    @classmethod
    def from_all_works_list(cls, li: Tag) -> "WorkNotice":
        title = li.find("a").get_text().strip()
        id_string = li.get("id").removeprefix("id")
        id = int(id_string)
        url = f"https://handschriftencensus.de/werke/{id_string}"
        return WorkNotice(id=id, title=title, url=url)

    @classmethod
    def from_tagged_works_list(cls, li: Tag) -> "WorkNotice":
        a = li.find("a")
        title = a.get_text().strip()
        href = a.get("href")
        id_string = href.split("/")[-1]
        id = int(id_string)
        url = f"https://handschriftencensus.de/werke/{id_string}"
        return WorkNotice(id=id, title=title, url=url)


class WorkModel(BaseModel):
    id: int
    title: str
    references: list[str | None] = Field(default=[])
    status: str | None = Field(default="unknown")

    @field_validator("status")
    def validate_status(cls, value: str | None):
        if value:
            assert value in TRADITION_STATUS
            return value
        else:
            raise ValueError(
                f"{value} must be 1 of the following: {', '.join(TRADITION_STATUS)}"
            )

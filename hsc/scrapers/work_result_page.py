from typing import Generator

from bs4 import BeautifulSoup, Tag

from hsc.models.witness import WitnessModel
from hsc.models.work import WorkModel

from .base import BaseScraperClass


class WorkResultPage:
    def __init__(self, html: bytes):
        self.__soup = BeautifulSoup(html, features="html.parser")
        self.__content = self.__soup.find("div", class_="content")
        assert self.__content is not None
        self._header: Tag = self.__content.find("h2")
        self._witnesses: Tag | None = self.__content.find("ol", class_="signaturen")

    def iter_witnesses(self) -> Generator[Tag, None, None]:
        if self._witnesses is not None:
            for witness in self._witnesses.find_all("li"):
                yield witness


class WorkMetadata(WorkResultPage, BaseScraperClass):
    def __init__(self, id: int, html: bytes):
        self.id = id
        super().__init__(html)
        # Properties
        self.status = self.get_status()
        self.title = self.get_title()
        self.references = self.get_references()

    def get_title(self):
        return self._header.text.strip()

    def get_references(self):
        return [a.get("href") for a in self._header.find_all("a")]

    def get_status(self) -> str:
        # If no witnesses were found, assume the text is lost
        if self._witnesses is None:
            return "lost"
        # Prepare to count the fragments
        fragments = 0
        for wit in self.iter_witnesses():
            status = wit.find("a").get("title").lower()
            # If any of the witnesses are complete, assume the text is surviving
            if "codex" in status:
                return "surviving"
            # If a witness is fragmentary, add it to the count
            elif "fragment" in status:
                fragments += 1
        # If none of the witnesses were complete but some where fragmentary,
        # assume the text is fragmentary
        if fragments > 0:
            return "fragmentary"

    def validate(self) -> WorkModel:
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        return WorkModel.model_validate(data)


class WitnessScraperOnWorksPage(WorkResultPage):
    def __init__(self, work_id: int, html: bytes):
        self.work_id = work_id
        super().__init__(html)

    def list_witnesses(self) -> list[WitnessModel]:
        witnesses = []
        for list_item in self.iter_witnesses():
            unit_relative_path = list_item.find_all("a")[1].get("href")
            ms_id = int(unit_relative_path.removeprefix("/"))
            status = list_item.find("a").get("title").lower()
            model = WitnessModel(work_id=self.work_id, ms_id=ms_id, status=status)
            witnesses.append(model)
        return witnesses

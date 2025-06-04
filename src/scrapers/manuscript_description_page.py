import re
from typing import Generator

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

from src.models.description import DescriptionModel
from src.models.document import DocumentModel

from .base import BaseScraperClass


class ManuscriptDescriptionPage:
    def __init__(self, html: bytes):
        self.__soup = BeautifulSoup(html, features="html.parser")
        self.places = self.__soup.find("table", id="places").find_all("tr", id=True)
        self.contents = self.__soup.find("h3", id="cInhalt").next_sibling.find(
            "td", id="inhalt"
        )
        codicology_header = self.__soup.find("h3", id="cKodikologie")
        empty_par = codicology_header.next_sibling
        codicology_table = empty_par.next_sibling
        assert codicology_table.name == "table"
        self.codicology = codicology_table.find_all("tr")

    @classmethod
    def group_by_line_break(cls, elements: Tag | list[Tag]) -> list[list]:
        if not isinstance(elements, list):
            elements = elements.contents
        # Determine the indices of the line breaks in the element list
        break_positions = [
            n
            for n, line in enumerate(elements)
            if isinstance(line, Tag) and line.name == "br"
        ]
        # If the elements don't have line breaks, return the list
        if len(break_positions) == 0:
            return [elements]
        # Set up the first grouping parameters
        start = 0
        groups = []
        # For each break point, slice a group from the element list
        for idx in break_positions:
            group = [
                elem
                for elem in elements[start:idx]
                if not (isinstance(elem, Tag) and elem.name == "br")
            ]
            groups.append(group)
            start = idx
        # Complete the groups with the last grouping
        group = [
            elem
            for elem in elements[start:]
            if not (isinstance(elem, Tag) and elem.name == "br")
        ]
        groups.append(group)
        return groups


class WitnessScraper(ManuscriptDescriptionPage):
    def __init__(self, html: bytes) -> None:
        super().__init__(html)

    def find_numbering(self, work_id: int) -> str | None:
        work_key = str(work_id)
        content_index = self.parse_contents()
        work_metadata = content_index.get(work_key)
        if work_metadata:
            for text_line in work_metadata:
                if (
                    isinstance(text_line, NavigableString)
                    and "Bl." in text_line
                    and "=" in text_line
                ):
                    foliation = re.search(
                        pattern=r"Bl.\s(.*)\s=|Bl.\s.(.*):", string=text_line
                    )
                    return foliation.group(1)

    def find_siglum(self, work_id: int) -> str | None:
        work_key = str(work_id)
        content_index = self.parse_contents()
        work_metadata = content_index.get(work_key)
        if work_metadata and isinstance(work_metadata[-1], NavigableString):
            match = re.search(pattern=r"(\(.\)$)", string=work_metadata[-1])
            if match:
                return match.group(1)

    @classmethod
    def elem_is_work_reference(cls, element: Tag | NavigableString) -> bool:
        if (
            isinstance(element, Tag)
            and element.name == "a"
            and "/werke/" in element.get("href")
        ):
            return True

    def parse_contents(self) -> dict:
        content_index = {}
        elements = [element for element in self.contents.contents]
        # If the contents contain line breaks, form groups of text lines
        groups = self.group_by_line_break(elements)
        if len(groups) > 0:
            for text_block in groups:
                for element in text_block:
                    if self.elem_is_work_reference(element=element):
                        key = element.get("href").split("/")[-1]
                        content_index.update({key: text_block})
        # If the contents did not contain any line breaks,
        # assume the contents are of only 1 item
        if content_index == {} and len(elements) > 0:
            for element in elements:
                if self.elem_is_work_reference(element=element):
                    key = element.get("href").split("/")[-1]
                    content_index.update({key: elements})
        return content_index


class DescriptionScraper(ManuscriptDescriptionPage, BaseScraperClass):
    writing_material = None
    folio_dimensions = None
    written_area = None
    number_of_columns = None
    number_of_lines = None
    stanza_layout = None
    verse_layout = None
    special_features = None
    date_of_creation = None
    scribal_dialect = None
    scriptorium_location = None

    def __init__(self, id: int, html: bytes) -> None:
        self.id = id
        super().__init__(html)
        self.parse_codicology_table()

    def validate(self) -> DescriptionModel:
        return DescriptionModel.model_validate(self.__dict__)

    @classmethod
    def get_text_from_group(cls, data) -> list:
        line_break_groups = cls.group_by_line_break(elements=data)
        groups = []
        for elem_list in line_break_groups:
            description = " ".join([elem.get_text() for elem in elem_list])
            groups.append(description)
        return groups

    def parse_codicology_table(self) -> None:
        for row in self.codicology:
            if not row.find("th"):
                continue
            header = row.find("th").get_text()
            data = row.find("td")
            if header == "Beschreibstoff":
                self.writing_material = data.get_text()
            elif header == "Blattgröße":
                self.folio_dimensions = self.get_text_from_group(data)
            elif header == "Schriftraum":
                self.written_area = self.get_text_from_group(data)
            elif header == "Spaltenzahl":
                self.number_of_columns = self.get_text_from_group(data)
            elif header == "Zeilenzahl":
                self.number_of_lines = self.get_text_from_group(data)
            elif header == "Strophengestaltung":
                self.stanza_layout = self.get_text_from_group(data)
            elif header == "Versgestaltung":
                self.verse_layout = self.get_text_from_group(data)
            elif header == "Besonderheiten":
                self.special_features = self.get_text_from_group(data)
            elif header == "Entstehungszeit":
                self.date_of_creation = data.get_text()
            elif header == "Schreibsprache":
                self.scribal_dialect = self.get_text_from_group(data)
            elif header == "Schreibort":
                self.scriptorium_location = self.get_text_from_group(data)


class DocumentScraper(ManuscriptDescriptionPage):
    def __init__(self, html: bytes, ms_id: int):
        self.ms_id = ms_id
        super().__init__(html)

    def list_documents(self) -> Generator[DocumentModel, None, None]:
        for table_row in self.places:
            doc_id = table_row.get("id")
            doc_type = self.get_type(tr=table_row)

            yield DocumentModel(
                id=doc_id,
                ms_id=self.ms_id,
                city=self.get_city(tr=table_row),
                institution=self.get_intitution(tr=table_row),
                shelfmark=self.get_shelfmark(tr=table_row),
                type=doc_type,
                numbering=self.get_numbering(tr=table_row),
            )

    @classmethod
    def _get_location_data(cls, tr: Tag) -> tuple[Tag, list[Tag]]:
        location_data = tr.find("td", class_="ort")
        links = location_data.find_all("a")
        return location_data, links

    @classmethod
    def get_city(cls, tr: Tag) -> str:
        location_data, links = cls._get_location_data(tr)
        city_link = links[0]
        href = city_link.get("href")
        return href.split("/")[-1]

    @classmethod
    def get_intitution(cls, tr: Tag) -> str:
        location_data, _ = cls._get_location_data(tr)
        parts = [part for part in location_data.children]
        institution_string: str = parts[1]
        s = institution_string.strip()
        s = s.removeprefix(", ")
        s = s.removesuffix(",")
        return s

    @classmethod
    def get_shelfmark(cls, tr: Tag) -> str:
        location_data, _ = cls._get_location_data(tr)
        parts = [part for part in location_data.children]
        return parts[-1].text

    @classmethod
    def get_type(cls, tr: Tag) -> str:
        return tr.find("td", class_="art").text

    @classmethod
    def get_numbering(cls, tr: Tag) -> str | None:
        data = tr.find("td", class_="umf")
        if data:
            return data.text

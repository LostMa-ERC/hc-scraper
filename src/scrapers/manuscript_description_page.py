import re

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

from src.models.physdesc import PhysDescModel


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
                    foliation = re.search(pattern=r"Bl.\s(.*)\s=", string=text_line)
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
        start, end = 0, 0
        elements = [element for element in self.contents.contents]
        # If the contents contain line breaks, form groups of text lines
        for n, line in enumerate(elements):
            end = n
            if isinstance(line, Tag) and line.name == "br":
                text_block = elements[start:end]
                for element in text_block:
                    if self.elem_is_work_reference(element=element):
                        key = element.get("href").split("/")[-1]
                        content_index.update({key: text_block})
                start = n
        # If the contents did not contain any line breaks,
        # assume the contents are of only 1 item
        if content_index == {} and len(elements) > 0:
            for element in elements:
                if self.elem_is_work_reference(element=element):
                    key = element.get("href").split("/")[-1]
                    content_index.update({key: elements})
        return content_index

    def get_siglum(self) -> str | None:
        pass


class PhysDescScraper(ManuscriptDescriptionPage):
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

    def validate(self) -> PhysDescModel:
        return PhysDescModel.model_validate(self.__dict__)

    def parse_codicology_table(self) -> None:
        for row in self.codicology:
            header = row.find("th").text.strip()
            data = row.find("td").text.strip()
            if header == "Beschreibstoff":
                self.writing_material = data
            elif header == "Blattgröße":
                self.folio_dimensions = data
            elif header == "schriftraum":
                self.written_area == data
            elif header == "Spaltenzahl":
                self.number_of_columns = data
            elif header == "Zeilenzahl":
                self.number_of_lines = data
            elif header == "Strophengestaltung":
                self.stanza_layout = data
            elif header == "Versgestaltung":
                self.verse_layout = data
            elif header == "Besonderheiten":
                self.special_features = data
            elif header == "Entstehungszeit":
                self.date_of_creation = data
            elif header == "Schreibsprache":
                self.scribal_dialect = data
            elif header == "Schreibort":
                self.scriptorium_location = data

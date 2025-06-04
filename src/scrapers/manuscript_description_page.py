from bs4 import BeautifulSoup

from src.models.codicology import CodicologyModel


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


class CodicologyScraper(ManuscriptDescriptionPage):
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

    def validate(self) -> CodicologyModel:
        return CodicologyModel.model_validate(self.__dict__)

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

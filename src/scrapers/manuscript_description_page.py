from bs4 import BeautifulSoup


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


class CodicologicalUnitScraper(ManuscriptDescriptionPage):
    def __init__(self, id: int, html: bytes):
        self.id = id
        super().__init__(html)

import unittest
from pathlib import Path

from rich import print

from src.scrapers.manuscript_description_page import (
    CodicologyScraper,
    ManuscriptDescriptionPage,
)

HTML_FILE = (
    Path(__file__).parent.joinpath("html").joinpath("manuscript_description_a.html")
)


class ManuDescriptionTest(unittest.TestCase):
    def setUp(self):
        with open(HTML_FILE) as f:
            html_bytes = f.read()
        self.scraper = ManuscriptDescriptionPage(html=html_bytes)

    def test_places(self):
        places = len(self.scraper.places)
        self.assertEqual(places, 2)

    def test_contents(self):
        contents = self.scraper.contents
        work_href = contents.find("a").get("href")
        self.assertEqual("/werke/221", work_href)

    def test_codicology(self):
        codicology = self.scraper.codicology
        print(codicology)
        self.assertGreater(len(codicology), 4)


class CodicologyTest(unittest.TestCase):
    def setUp(self):
        with open(HTML_FILE) as f:
            html_bytes = f.read()
        self.scraper = CodicologyScraper(id=4204, html=html_bytes)

    def test(self):
        model = self.scraper.validate()
        self.assertEqual(model.writing_material, "Papier")
        self.assertEqual(model.number_of_columns, "1")
        self.assertEqual(model.number_of_lines, "36-48")
        self.assertEqual(model.id, 4204)


if __name__ == "__main__":
    unittest.main()

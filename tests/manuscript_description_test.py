import unittest
from pathlib import Path

from hsc.scrapers.manuscript_description_page import (
    DescriptionScraper,
    ManuscriptDescriptionPage,
)

SIMPLE_HTML_FILE = (
    Path(__file__).parent.joinpath("html").joinpath("manuscript_description_4204.html")
)

NESTED_HTML_FILE = (
    Path(__file__).parent.joinpath("html").joinpath("manuscript_description_2995.html")
)


class BaseDescriptionPageTest(unittest.TestCase):
    def setUp(self):
        with open(SIMPLE_HTML_FILE) as f:
            html_bytes = f.read()
        self.scraper = ManuscriptDescriptionPage(html=html_bytes)

    def test_places(self):
        places = len(self.scraper.places)
        self.assertEqual(places, 2)

    def test_contents(self):
        contents = self.scraper.content_row
        work_href = contents.find("a").get("href")
        self.assertEqual("/werke/221", work_href)

    def test_codicology(self):
        codicology = self.scraper.codicology
        self.assertGreater(len(codicology), 4)


class DescriptionTest(unittest.TestCase):
    def setUp(self):
        with open(SIMPLE_HTML_FILE) as f:
            self.html_simple = f.read()
        with open(NESTED_HTML_FILE) as f:
            self.html_nested = f.read()

    def test_simple(self):
        scraper = DescriptionScraper(id=4204, html=self.html_simple)
        model = scraper.validate()
        self.assertEqual(model.writing_material, "Papier")
        self.assertEqual(model.number_of_columns[0], "1")
        self.assertEqual(model.number_of_lines[0], "36-48")
        self.assertEqual(model.id, 4204)
        self.assertEqual(model.written_area[0], "245-250 x 145 mm")

    def test_nested(self):
        scraper = DescriptionScraper(id="2995", html=self.html_nested)
        model = scraper.validate()
        two_column_descriptions = ["Bl. 1-22: 3 ", "Bl. 23-108: 2"]
        self.assertEqual(model.number_of_columns, two_column_descriptions)

    def test_contents(self):
        scraper = DescriptionScraper(id="2995", html=self.html_nested)
        contents = scraper.contents
        self.assertEqual(["Wolfram von Eschenbach: 'Parzival' (U [Gμ])"], contents)


if __name__ == "__main__":
    unittest.main()

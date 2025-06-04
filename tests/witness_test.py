import unittest
from pathlib import Path

from src.scrapers.manuscript_description_page import WitnessScraper

HTML_WITH_NUMBERING = (
    Path(__file__).parent.joinpath("html").joinpath("manuscript_description_b.html")
)

HTML_WITH_SIGLUM = (
    Path(__file__).parent.joinpath("html").joinpath("manuscript_description_a.html")
)


class WitnessTest(unittest.TestCase):
    def setUp(self):
        with open(HTML_WITH_NUMBERING) as f:
            self.html_with_numbering = f.read()
        with open(HTML_WITH_SIGLUM) as f:
            self.html_with_siglum = f.read()

    def test_Kalendar(self):
        scraper = WitnessScraper(html=self.html_with_numbering)
        numbering = scraper.find_numbering(work_id=526)
        siglum = scraper.find_siglum(work_id=526)
        self.assertEqual(numbering, "1-12")
        self.assertIsNone(siglum)

    def test_Getijdenboek(self):
        scraper = WitnessScraper(html=self.html_with_numbering)
        numbering = scraper.find_numbering(work_id=2295)
        siglum = scraper.find_siglum(work_id=2295)
        self.assertEqual(numbering, "1r-175r")
        self.assertIsNone(siglum)

    def test_Mariengebet(self):
        scraper = WitnessScraper(html=self.html_with_numbering)
        numbering = scraper.find_numbering(work_id=3239)
        siglum = scraper.find_siglum(work_id=3239)
        self.assertEqual(numbering, "180r-180v")
        self.assertIsNone(siglum)

    def test_lancelot(self):
        scraper = WitnessScraper(html=self.html_with_siglum)
        numbering = scraper.find_numbering(work_id=221)
        siglum = scraper.find_siglum(work_id=221)
        self.assertIsNone(numbering)
        self.assertEqual("(p)", siglum)


if __name__ == "__main__":
    unittest.main()

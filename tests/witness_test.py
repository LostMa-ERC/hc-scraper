import unittest
from pathlib import Path

from src.scrapers.manuscript_description_page import WitnessScraper

HTML_WITH_NUMBERING = (
    Path(__file__).parent.joinpath("html").joinpath("manuscript_description_21835.html")
)

HTML_WITH_SIGLUM = (
    Path(__file__).parent.joinpath("html").joinpath("manuscript_description_4204.html")
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


class TempTest(unittest.TestCase):
    def setUp(self):
        with open(HTML_WITH_NUMBERING) as f:
            self.html_with_numbering = f.read()
        with open(HTML_WITH_SIGLUM) as f:
            self.html_with_siglum = f.read()

    def confirm_that_grouping_by_line_break_completed(self, contents):
        groups = WitnessScraper.group_by_line_break(elements=contents)
        last_element = [elem for elem in contents.children][-1]
        last_group = groups[-1][-1]
        self.assertEqual(last_element, last_group)

    def test_content_list(self):
        scraper = WitnessScraper(html=self.html_with_numbering)
        contents = scraper.contents
        self.confirm_that_grouping_by_line_break_completed(contents=contents)

    def test_content_single_item(self):
        scraper = WitnessScraper(html=self.html_with_siglum)
        contents = scraper.contents
        self.confirm_that_grouping_by_line_break_completed(contents=contents)


if __name__ == "__main__":
    unittest.main()

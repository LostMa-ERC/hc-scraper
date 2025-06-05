import unittest
from pathlib import Path

from hsc.scrapers.manuscript_description_page import DocumentScraper

HTML_FILE = (
    Path(__file__).parent.joinpath("html").joinpath("manuscript_description_2995.html")
)


class DocumentTest(unittest.TestCase):
    def setUp(self):
        with open(HTML_FILE) as f:
            html = f.read()
            self.scraper = DocumentScraper(html=html, ms_id=2995)

    def test(self):
        for doc in self.scraper.list_documents():
            self.assertIsNotNone(doc.shelfmark)


if __name__ == "__main__":
    unittest.main()

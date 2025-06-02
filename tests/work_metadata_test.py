import unittest
from pathlib import Path

from src.scrapers.works import WorkMetadata

WORKS_PAGE_A = Path(__file__).parent.joinpath("work_a.html")
WORKS_PAGE_B = Path(__file__).parent.joinpath("work_b.html")
WORKS_PAGE_C = Path(__file__).parent.joinpath("work_c.html")

# Psalm fragment
with open(WORKS_PAGE_A) as f:
    work_a_html = f.read()
work_a_id = 2639

# Parzifal, many witnesses
with open(WORKS_PAGE_B) as f:
    work_b_html = f.read()
work_b_id = 437

# Verweis, no witnesses
with open(WORKS_PAGE_C) as f:
    work_c_html = f.read()
work_c_id = 2193


class WorkMetadataTest(unittest.TestCase):
    def test_a(self):
        wm = WorkMetadata(id=work_a_id, html=work_a_html)
        model = wm.validate()
        self.assertEqual(model.status, "fragmentary")

    def test_b(self):
        wm = WorkMetadata(id=work_b_id, html=work_b_html)
        model = wm.validate()
        self.assertEqual(model.status, "surviving")

    def test_c(self):
        wm = WorkMetadata(id=work_c_id, html=work_c_html)
        model = wm.validate()
        self.assertEqual(model.status, "lost")


if __name__ == "__main__":
    unittest.main()

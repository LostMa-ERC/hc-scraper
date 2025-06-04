import unittest

import requests

from src.actions import list_work_notices, scrape_one_work
from src.database import Database
from src.models.work import WorkNotice

work_notices = [
    WorkNotice(
        id="2639",
        title="irrelevant",
        url="https://handschriftencensus.de/werke/2639",
    ),
    WorkNotice(
        id="2639",
        title="duplicate",
        url="https://handschriftencensus.de/werke/2639",
    ),
    WorkNotice(
        id="437",
        title="irrelevant",
        url="https://handschriftencensus.de/werke/437",
    ),
    WorkNotice(
        id="2193",
        title="irrelevant",
        url="https://handschriftencensus.de/werke/2193",
    ),
]


class WorkMetadataTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def test(self):
        with requests.session() as session:
            for work_notice in work_notices:
                try:
                    scrape_one_work(
                        db=self.db, work_notice=work_notice, session=session
                    )
                except Exception as e:
                    print(work_notice)
                    raise e
        n_works = self.db.conn.table("Works").count("id").fetchone()[0]
        self.assertEqual(n_works, 3)


class WorkListTest(unittest.TestCase):
    def test_all_works(self):
        urls = ["https://handschriftencensus.de/werke"]
        with requests.session() as session:
            notices = list_work_notices(work_pages=urls, session=session)
        self.assertGreater(len(notices), 500)
        self.assertIsInstance(notices[0], WorkNotice)

    def test_tagged_works(self):
        urls = ["https://handschriftencensus.de/tag/Antiken-+und+Alexanderroman"]
        with requests.session() as session:
            notices = list_work_notices(work_pages=urls, session=session)
        self.assertGreater(len(notices), 20)
        self.assertLess(len(notices), 100)
        self.assertIsInstance(notices[0], WorkNotice)


if __name__ == "__main__":
    unittest.main()

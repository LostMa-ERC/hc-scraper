import unittest
import requests

from src.models.work import PartialWork
from src.main import scrape_work
from src.database import Database

work_notices = [
    PartialWork(
        id="2639",
        title="irrelevant",
        url="https://handschriftencensus.de/werke/2639",
    ),
    PartialWork(
        id="2639",
        title="duplicate",
        url="https://handschriftencensus.de/werke/2639",
    ),
    PartialWork(
        id="437",
        title="irrelevant",
        url="https://handschriftencensus.de/werke/437",
    ),
    PartialWork(
        id="2193",
        title="404 error",
        url="https://handschriftencensus.de/werke/2193",
    ),
]


class WorkTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def test(self):
        with requests.session() as session:
            for work_notice in work_notices:
                try:
                    scrape_work(db=self.db, work_notice=work_notice, session=session)
                except Exception as e:
                    print(work_notice)
                    raise e
        n_works = self.db.conn.table("Works").count("id").fetchone()[0]
        self.assertEqual(n_works, 2)


if __name__ == "__main__":
    unittest.main()

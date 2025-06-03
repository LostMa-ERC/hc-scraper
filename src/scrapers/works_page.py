from bs4 import BeautifulSoup
from src.models.work import WorkNotice


class AllWorksPage:
    def __init__(self, html: bytes):
        self.soup = BeautifulSoup(html, features="html.parser")

    def get_works(self):
        for unordered_list in self.soup.find_all(
            "ul", class_="werke quicksearch_container"
        ):
            for list_item in unordered_list.find_all("li"):
                yield WorkNotice.from_all_works_list(li=list_item)

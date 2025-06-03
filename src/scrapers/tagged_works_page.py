from bs4 import BeautifulSoup

from src.models.work import WorkNotice


class TaggedWorksPage:
    def __init__(self, html: bytes):
        self.soup = BeautifulSoup(html, features="html.parser")

    def get_works(self):
        werke_h3 = self.soup.find("h3", id="werke")
        unordered_list = werke_h3.next_sibling
        for list_item in unordered_list.find_all("li"):
            yield WorkNotice.from_tagged_works_list(li=list_item)

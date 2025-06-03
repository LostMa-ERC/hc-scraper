from bs4 import BeautifulSoup


class TagsPage:
    def __init__(self, html: bytes):
        self.soup = BeautifulSoup(html, features="html.parser")

    def iterate_tags(self):
        for unordered_list in self.soup.find_all("ul"):
            for list_item in unordered_list.find_all("li"):
                href = list_item.find("a").get("href")
                yield list_item.text, f"https://handschriftencensus.de{href}"

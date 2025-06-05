import requests
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from hsc.scrapers.tags_page import TagsPage


class TagPrompt:
    def __init__(self, session: requests.session):
        resp = session.get("https://handschriftencensus.de/tags")
        self.page = TagsPage(html=resp.content)
        self.urls = []
        self._asked = []
        self._options = [(tag, url) for tag, url in self.page.iterate_tags()]

    def choose_tags(self):
        console = Console()
        for tag, url in self._options:
            console.clear()
            table = self.regenerate_table()
            console.print(table)
            console.print("Select the tag")
            self._asked.append(tag)
            if Confirm.ask(tag, console=console):
                self.urls.append(url)
        return self.urls

    def regenerate_table(self):
        table = Table()
        table.add_column("Tag")
        table.add_column("Selected")

        for tag, url in self._options:
            if url in self.urls:
                row = (tag, "[green]Yes")
            elif tag in self._asked:
                row = (tag, "[red]No")
            else:
                row = (tag, None)
            table.add_row(*row)
        return table

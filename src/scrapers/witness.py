from .works import WorkResultPage


class WitnessScraper(WorkResultPage):
    def __init__(self, html: bytes):
        super().__init__(html)

    def get_codicological_unit(self):
        for list_item in self.iter_witnesses():
            unit_relative_path = list_item.find_all("a")[1].get("href")
            unit_id = int(unit_relative_path.removeprefix("/"))
            yield unit_id

import requests

from hsc.models.work import WorkNotice
from hsc.scrapers.tagged_works_page import TaggedWorksPage
from hsc.scrapers.works_page import AllWorksPage


def list_work_notices(
    work_pages: list[str], session: requests.Session
) -> list[WorkNotice]:
    work_notices = []
    for url in work_pages:
        resp = session.get(url)
        html = resp.content
        if "/tag" in url:
            scraper = TaggedWorksPage(html=html)
        else:
            scraper = AllWorksPage(html=html)
        work_notices.extend([w for w in scraper.get_works()])
    return work_notices

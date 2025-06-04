import requests

from src.database import Database
from src.scrapers.manuscript_description_page import DescriptionScraper, WitnessScraper


def scrape_manuscript_page(
    ms: int, works: list[int], session: requests.session, db: Database
):
    url = f"https://handschriftencensus.de/{ms}"
    resp = session.get(url)
    if resp.status_code == 404:
        return
    html = resp.content

    # Model and insert the manuscript description
    try:
        witness_scraper = WitnessScraper(html=html)
        description = DescriptionScraper(id=ms, html=html).validate()
    except Exception as e:
        print(url)
        raise e
    db.update_manuscript_description(data=description.model_dump())
    # For each work in the manuscript, try to update its siglum
    for work_id in works:
        siglum = witness_scraper.find_siglum(work_id=work_id)
        if siglum:
            sql = "update Witness set siglum = ? where work_id = ? and ms_id = ?"
            params = [siglum, work_id, ms]
            db.conn.execute(sql, parameters=params)

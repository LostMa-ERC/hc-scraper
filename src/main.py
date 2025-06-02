import requests
import click
from rich.progress import (
    Progress,
    BarColumn,
    MofNCompleteColumn,
    TextColumn,
    TimeElapsedColumn,
)

from src.scrapers.works import WorksPage, WorkMetadata
from src.scrapers.witness import WitnessScraper
from src.database import Database

DB_PATH = "hc.duckdb"


@click.group()
def cli():
    pass


@cli.command("works")
def works():
    db = Database(db_path=DB_PATH)
    with (
        requests.session() as session,
        Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        ) as p,
    ):
        # Get the latest list of works from the HC website
        resp = session.get("https://handschriftencensus.de/werke")
        works_page_html = resp.content
        works_page_scraper = WorksPage(html=works_page_html)
        work_notices = [w for w in works_page_scraper.get_works()]

        # Set up a progress bar to track the scraping of all the works
        t = p.add_task("Scraping works...", total=len(work_notices))

        # Iterate through the scraped works' notices
        for work_notice in work_notices:
            # Only if the work is not yet in the database, scrape it
            if db.work_is_present(id=work_notice.id) is False:
                # Fetch the work's result page
                resp = session.get(work_notice.url)
                html = resp.content

                # Model and insert the work metadata
                work_model = WorkMetadata(id=work_notice.id, html=html).validate()
                metadata = work_model.model_dump()
                db.insert_work(data=metadata)

                # Model and insert the witness metadata
                for witness_doc in WitnessScraper(html=html).get_codicological_unit():
                    if db.witness_is_present(work_notice.id, witness_doc) is False:
                        db.insert_witness(work_id=work_notice.id, unit_id=witness_doc)

            p.advance(t)


if __name__ == "__main__":
    cli()

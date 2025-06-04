import click
import requests
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

from src.actions import (
    TagPrompt,
    list_work_notices,
    scrape_manuscript_page,
    scrape_one_work,
)
from src.database import Database

DB_PATH = "hsc.duckdb"


@click.group()
def cli():
    pass


@cli.command("ms")
def manuscripts():
    db = Database(db_path=DB_PATH)
    # Count manuscripts for progress bar
    total = db.count_all_manuscripts()
    completed = db.count_completed_manuscripts()
    # Get the manuscripts and their relevant works
    uncompleted = db.get_manuscripts_and_works()
    with (
        requests.session() as session,
        Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        ) as p,
    ):
        t = p.add_task("Scraping", total=total, completed=completed)
        # Get the manuscripts and their relevant works
        for data in uncompleted:
            ms_id, works = data
            scrape_manuscript_page(ms=ms_id, works=works, session=session, db=db)
            p.advance(t)


@cli.command("works")
@click.option("--choose-tags", is_flag=True, default=False)
@click.option("-t", "--tag")
def works(choose_tags: bool, tag: str | None):
    db = Database(db_path=DB_PATH)
    with requests.session() as session:
        # Get the latest list of works from the HC website
        if choose_tags:
            prompter = TagPrompt(session=session)
            urls = prompter.choose_tags()
        elif tag:
            urls = [f"https://handschriftencensus.de/tag/{tag}"]
        else:
            urls = ["https://handschriftencensus.de/werke"]
        work_notices = list_work_notices(work_pages=urls, session=session)

        with Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        ) as p:
            # Set up a progress bar to track the scraping of all the works
            t = p.add_task("Scraping works...", total=len(work_notices))

            # Iterate through the scraped works' notices
            for work_notice in work_notices:
                scrape_one_work(db=db, work_notice=work_notice, session=session)
                p.advance(t)


if __name__ == "__main__":
    cli()

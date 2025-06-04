import requests

from src.database import Database
from src.models.work import WorkNotice
from src.scrapers.work_result_page import WitnessScraperOnWorksPage, WorkMetadata


def scrape_work(db: Database, work_notice: WorkNotice, session: requests.Session):
    # Only if the work is not yet in the database, scrape it
    if db.work_is_present(id=work_notice.id) is False:
        # Fetch the work's result page
        resp = session.get(work_notice.url)
        if resp.status_code == 404:
            return
        html = resp.content

        # Model and insert the work metadata
        work_model = WorkMetadata(id=work_notice.id, html=html).validate()
        metadata = work_model.model_dump()
        db.create_work(data=metadata)

        # Model and insert the witness metadata
        for witness in WitnessScraperOnWorksPage(
            work_id=work_model.id, html=html
        ).list_witnesses():
            if db.witness_is_present(witness.work_id, witness.unit_id) is False:
                metadata = witness.model_dump()
                db.create_witness(metadata)

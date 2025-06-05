from pydantic import BaseModel, Field


class DocumentModel(BaseModel):
    id: str
    ms_id: int
    shelfmark: str
    type: str
    city: str
    institution: str
    numbering: str = Field(default=None)

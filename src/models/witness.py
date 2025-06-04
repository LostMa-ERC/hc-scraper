from pydantic import BaseModel, Field


class WitnessModel(BaseModel):
    work_id: int
    ms_id: int
    status: str
    siglum: str | None = Field(default=None)

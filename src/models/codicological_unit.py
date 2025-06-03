from pydantic import BaseModel, Field


class CodicologicalUnitModel(BaseModel):
    id: int
    writing_material: str = Field(default=None)
    folio_dimensions: str = Field(default=None)
    written_area: str = Field(default=None)
    number_of_columns: str = Field(default=None)
    number_of_lines: str = Field(default=None)
    special_features: str = Field(default=None)
    verse_layout: str = Field(default=None)
    date_of_creation: str = Field(default=None)
    scribal_dialect: str = Field(default=None)
    scriptorium_location: str = Field(default=None)

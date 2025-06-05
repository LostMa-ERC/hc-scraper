from pydantic import BaseModel, Field


class DescriptionModel(BaseModel):
    id: int
    writing_material: str = Field(default=None)  # Beschreibstoff
    folio_dimensions: list[str] = Field(default=[])  # Blattgröße
    written_area: list[str] = Field(default=[])  # Schriftraum
    number_of_columns: list[str] = Field(default=[])  # Spaltenzahl
    number_of_lines: list[str] = Field(default=[])  # Zeilenzahl
    stanza_layout: list[str] = Field(default=[])  # Strophengestaltung
    verse_layout: list[str] = Field(default=[])  # Versgestaltung
    special_features: list[str] = Field(default=[])  # Besonderheiten
    date_of_creation: list[str] = Field(default=[])  # Entstehungszeit
    scribal_dialect: list[str] = Field(default=[])  # Schreibsprache
    scriptorium_location: list[str] = Field(default=[])  # Schreibort
    contents: list[str] = Field(default=[])

from pydantic import BaseModel, Field


class DescriptionModel(BaseModel):
    id: int
    writing_material: str = Field(default=None)  # Beschreibstoff
    folio_dimensions: str = Field(default=None)  # Blattgröße
    written_area: str = Field(default=None)  # Schriftraum
    number_of_columns: str = Field(default=None)  # Spaltenzahl
    number_of_lines: str = Field(default=None)  # Zeilenzahl
    stanza_layout: str = Field(default=None)  # Strophengestaltung
    verse_layout: str = Field(default=None)  # Versgestaltung
    special_features: str = Field(default=None)  # Besonderheiten
    date_of_creation: str = Field(default=None)  # Entstehungszeit
    scribal_dialect: str = Field(default=None)  # Schreibsprache
    scriptorium_location: str = Field(default=None)  # Schreibort

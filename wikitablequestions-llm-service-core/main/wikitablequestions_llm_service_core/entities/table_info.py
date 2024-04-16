from pydantic import BaseModel, Field


class TableInfo(BaseModel):
    """Information regarding a structured table."""

    table_name: str = Field(
        ..., description="table name (must be underscores and NO spaces)"
    )
    summary: str = Field(..., description="short, concise summary/caption of the table")

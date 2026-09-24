from pydantic import BaseModel, PositiveInt


class ExtractedPage(BaseModel):
    page: PositiveInt | None
    content: str


class ExtractedDocument(BaseModel):
    title: str
    source: str
    pages: list[ExtractedPage]

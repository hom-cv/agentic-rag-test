from pathlib import Path

import pymupdf4llm
from schemas.extraction import ExtractedDocument, ExtractedPage


class ExtractionService:
    def extract_file(self, path: Path, source: str) -> ExtractedDocument:
        if path.suffix.lower() == ".pdf":
            pdf_pages = pymupdf4llm.to_markdown(
                str(path), page_chunks=True, use_ocr=False
            )

            if not isinstance(pdf_pages, list):
                raise TypeError("Expected a list of PDF pages")

            pages = []
            for number, page in enumerate(pdf_pages, start=1):
                pages.append(ExtractedPage(page=number, content=page["text"]))
        else:
            pages = [ExtractedPage(
                page=None, content=path.read_text(encoding="utf-8-sig")
            )]

        return ExtractedDocument(title=path.stem, source=source, pages=pages)

from pathlib import Path

import pymupdf4llm


class ExtractionService:
    def extract_file(self, path: Path, source: str) -> dict:
        if path.suffix.lower() == ".pdf":
            pdf_pages = pymupdf4llm.to_markdown(
                str(path), page_chunks=True, use_ocr=False
            )

            if not isinstance(pdf_pages, list):
                raise TypeError("Expected a list of PDF pages")

            pages = []

            for number, page in enumerate(pdf_pages, start=1):
                pages.append({"page": number, "content": page["text"]})
        else:
            pages = [{"page": None, "content": path.read_text(encoding="utf-8-sig")}]

        return {
            "title": path.stem,
            "source": source,
            "pages": pages,
        }

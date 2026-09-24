from uuid import uuid4

from langchain_text_splitters import (
    MarkdownTextSplitter,
    RecursiveCharacterTextSplitter,
)


class ChunkingService:
    def __init__(self) -> None:
        self.parent_splitter = MarkdownTextSplitter(
            chunk_size=6000,
            chunk_overlap=0,
            is_separator_regex=True,
            add_start_index=True,
            strip_whitespace=False,
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=160,
            add_start_index=True,
            strip_whitespace=False,
        )

    def chunk_document(self, document: dict) -> dict:
        text = ""
        page_ranges = []
        for page in document["pages"]:
            start = len(text)
            text += page["content"]
            page_ranges.append((start, len(text), page["page"]))
            text += "\n\n"

        parents = []
        for parent in self.parent_splitter.create_documents([text]):
            parent_id = str(uuid4())
            parent_start = parent.metadata["start_index"]
            children = []

            for child in self.child_splitter.create_documents([parent.page_content]):
                child_start = parent_start + child.metadata["start_index"]
                children.append({
                    "id": str(uuid4()),
                    "parent_id": parent_id,
                    "content": child.page_content,
                    "pages": self.page_numbers(
                        child_start, len(child.page_content), page_ranges
                    ),
                })

            parents.append({
                "id": parent_id,
                "content": parent.page_content,
                "pages": self.page_numbers(
                    parent_start, len(parent.page_content), page_ranges
                ),
                "children": children,
            })

        return {
            "title": document["title"],
            "source": document["source"],
            "parents": parents,
        }

    @staticmethod
    def page_numbers(start: int, length: int, page_ranges: list) -> list[int]:
        """Find the source pages that overlap a chunk's character range."""
        pages = []
        for page_start, page_end, number in page_ranges:
            if number is None or page_start == page_end:
                continue
            if start < page_end and start + length > page_start:
                pages.append(number)
        return pages

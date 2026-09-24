from pathlib import Path

from schemas.extraction import ExtractedDocument
from services.chunking_service import ChunkingService


def main() -> None:
    chunker = ChunkingService()

    for path in sorted(Path(".").glob("*_extract.json")):
        document = ExtractedDocument.model_validate_json(path.read_text(encoding="utf-8"))
        transformed = chunker.chunk_document(document)

        name = path.name.removesuffix("_extract.json")
        output_path = Path(f"{name}_transform.json")
        output_path.write_text(
            transformed.model_dump_json(indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()

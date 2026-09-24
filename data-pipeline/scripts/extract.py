import json
from pathlib import Path

from services.extraction_service import ExtractionService
from services.file_reader_service import FileReaderService


def main() -> None:
    reader = FileReaderService()
    extractor = ExtractionService()

    for path in reader.list_files():
        document = extractor.extract_file(path, path.name)
        output_path = Path(f"{path.stem}_extract.json")
        output_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()

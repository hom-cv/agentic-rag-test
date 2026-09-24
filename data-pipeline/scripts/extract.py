import json
from pathlib import Path

from services.extraction_service import ExtractionService
from services.file_reader_service import FileReaderService


def main() -> None:
    reader = FileReaderService()
    extractor = ExtractionService()

    for path in reader.list_files():
        source = path.relative_to(reader.files_dir)
        document = extractor.extract_file(path, source.as_posix())

        output_path = Path("output") / source.with_suffix(source.suffix + ".json")

        output_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()

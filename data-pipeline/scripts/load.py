from pathlib import Path

from schemas.transform import TransformedDocument
from services.load_service import LoadService


def main() -> None:
    loader = LoadService()

    for path in sorted(Path(".").glob("*_transform.json")):
        document = TransformedDocument.model_validate_json(path.read_text(encoding="utf-8"))
        document_id = loader.load_document(document)

        print(f"Loaded {document.source}: {document_id}")


if __name__ == "__main__":
    main()

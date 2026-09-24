"""Read local source documents for the ingestion pipeline."""

from pathlib import Path

FILES_DIR = Path("input")
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


class FileReaderService:
    def __init__(self, files_dir: str | Path = FILES_DIR) -> None:
        self.files_dir = Path(files_dir).resolve()

    def list_files(self) -> list[Path]:
        """Return supported input files, sorted by path."""
        if not self.files_dir.is_dir():
            raise NotADirectoryError(self.files_dir)

        files = []

        for path in self.files_dir.glob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            files.append(path)

        return sorted(files)

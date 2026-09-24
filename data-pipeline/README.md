# Data Pipeline

Put `.pdf`, `.txt`, and `.md` files in `files/`. Run from this directory:

```sh
pipenv sync
pipenv run python -m scripts.extract
```

Writes one JSON per document to `output/`, with its title, source, and page content.
For example, `files/notes/report.pdf` becomes `output/notes/report.pdf.json`.
Rerunning replaces the corresponding output files.
PDFs become Markdown with page numbers. Text files use `null` for the page.
OCR is disabled. Chunking and ingestion come next.

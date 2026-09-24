# Data Pipeline

Put `.pdf`, `.txt`, and `.md` files directly in `input/`, using unique base names.
Run from this directory:

```sh
pipenv sync
cp .env_template .env
```

Set `OPENAI_API_KEY` and your PostgreSQL credentials in `.env`.
Apply migrations from `backend/` with `pipenv run alembic upgrade head`.
Then regenerate models from `data-pipeline/`:

```sh
pipenv run python -m scripts.generate_models
```

This generates `models.py` using sqlacodegen. Rerun after schema changes; do not
edit the generated file manually. Run the pipeline commands from this directory.

```sh
pipenv run python -m scripts.extract
pipenv run python -m scripts.transform
pipenv run python -m scripts.load
```

`input/report.pdf` produces `report_extract.json` and `report_transform.json`
in this directory. Rerunning replaces those outputs.

Extract preserves text and PDF page references; OCR is disabled.
Transform creates parents of up to 6,000 characters and children of up to 1,200
characters, with up to 160 characters of child overlap. It sends child text to
OpenAI's `text-embedding-3-small` and stores 1,536-dimensional embeddings in the
transform JSON. Rerunning transform makes new paid embedding calls.

Load reads `*_transform.json` and saves documents, parent chunks, and embedded
child chunks to PostgreSQL. Page numbers are stored as JSON text in
`source_location`. Each document loads in one transaction; loading the same
source again replaces its chunks and preserves its document ID.

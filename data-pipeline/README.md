# Data Pipeline

Put `.pdf`, `.txt`, and `.md` files directly in `input/`, using unique base names.
Run from this directory:

```sh
pipenv sync
pipenv run python -m scripts.extract
pipenv run python -m scripts.transform
```

`input/report.pdf` produces `report_extract.json` and `report_transform.json`
in this directory. Rerunning replaces those outputs.

Extraction preserves text and PDF page references; OCR is disabled.
Transform creates parents of up to 6,000 characters and children of up to 1,200
characters, with up to 160 characters of child overlap. Embedding comes later.

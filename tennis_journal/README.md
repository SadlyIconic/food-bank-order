# Tennis Journal

A simple Flask app for logging tennis matches — opponent, date, score, and notes. Data persists in `entries.json`.

## Requirements

- Python 3.10 or newer

## Run

```bash
cd tennis_journal
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The `entries.json` file is created after the first save.

On Windows, if `python` is not found, try:

```bash
py app.py
```

## Features

- Create, view, edit, and delete match entries
- Entries sorted by match date (newest first)
- Search by opponent name on the home page (`?q=...`)
- Win/loss and singles/doubles fields
- JSON persistence across server restarts

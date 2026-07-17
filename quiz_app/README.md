# Python Quiz App

A simple multiple-choice quiz with a graphical interface built using Tkinter (included with Python).

## Requirements

- Python 3.10 or newer
- Tkinter (bundled with standard Python on Windows)

## Run

```bash
cd quiz_app
python quiz_app.py
```

On Windows, if `python` is not found, try:

```bash
py quiz_app.py
```

## Customize

Edit `questions.json` to add or change questions. Each entry needs:

- `question` — the question text
- `options` — list of answer choices
- `answer` — zero-based index of the correct option

## Features

- Welcome screen and progress bar
- Multiple-choice questions with radio buttons
- Instant feedback after each answer
- Final score with percentage
- Play again without restarting the app

# CalcLab

A safe expression calculator with a command-line REPL, a REST API and a
responsive, keyboard-friendly web UI. Built for **UCS 745 - Cloud and DevOps
(Lab Assignment, Q1)** to practise real-world Git workflows: feature branches,
pull/push, CI, merging and conflict resolution.

## Features

- Hand-written tokenizer and recursive-descent parser (no `eval`), with correct
  operator precedence and clear, position-aware error messages
- Operators `+ - * / % ^` (also `**`), brackets and unary minus
- REST API plus a responsive web UI with full keyboard support
- Resource limits (expression length, nesting depth, exponent size)
- SQLite-backed calculation history, an `ans` variable (previous result) and a light/dark theme

## Architecture

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Core | `calclab/engine.py`, `functions.py`, `errors.py` | Pure Python, no web dependencies; parses and evaluates expressions |
| API | `calclab/api.py` | Flask app factory and JSON endpoints |
| UI | `static/` | HTML, CSS and vanilla JavaScript talking to the API |
| CLI | `calclab/cli.py` | `python -m calclab` REPL |

## Getting started

    python -m venv .venv
    .venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    python run.py                   # open http://127.0.0.1:5000
    python -m calclab               # or use the command-line REPL

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Service status and version |
| POST | `/api/evaluate` | Body `{"expression": "2+3*4"}` returns `{"ok": true, "result": 14, "display": "14"}`; errors return HTTP 400 with `{"ok": false, "error": "..."}` |

## Tests and CI

    python -m unittest discover -s tests -t . -v

GitHub Actions (`.github/workflows/ci.yml`) runs the suite on Python 3.10 and
3.12 for every push and pull request. An optional `Dockerfile` is included
(`docker build -t calclab . && docker run -p 5000:5000 calclab`).

# AI Study Helper

This is an app to help you with your studies! It uses AI locally to build flashcards and test your knowledge.

## Getting started

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements
```

Create the database:

```bash
createdb ai-study-helper
```

Rename `.env.example` to `.env` and adjust the `DATABASE_URL` (if needed).

Run the database migrations:

```bash
alembic upgrade head
```

For running the app, I recommend you use vscode. The `launch.json` is configured already, so you should be able to just start the debugger.

If you don't want to use vscode for any reason, you can run the app in the terminal:

```bash
uvicorn app.main:app --reload
```

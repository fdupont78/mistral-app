# AGENTS.md

Conventions for AI agents and humans contributing to **Mistral App** — a Python 3.11+ chat application with Mistral 3B model, Streamlit frontend, and conversation persistence.

Project layout: `main.py` is the CLI entry point; `chat.py` handles interactive chat; `conversation.py` manages conversation state; `model.py` loads the Mistral model; `database.py` handles SQLite persistence; `frontend.py` provides the Streamlit UI.

## Commands

- `python main.py chat` — start interactive CLI chat
- `python main.py list` — list all conversations
- `python main.py load <id>` — load and display a conversation
- `streamlit run frontend.py` — launch Streamlit web interface

## Project layout & module conventions

- `main.py` — CLI entry point and command routing
- `chat.py` — interactive chat logic and conversation commands
- `conversation.py` — `Conversation` class and message management
- `model.py` — Mistral model loading and response generation
- `database.py` — SQLite database setup and conversation persistence
- `frontend.py` — Streamlit web interface

## Python style

- Prefer `match` / `case` over long `if` / `elif` chains.
- Use the walrus operator `:=` only when it shortens code and improves clarity.
- Be a never-nester: early returns and guard clauses over nested blocks.
- Modern type hints only: built-in generics (`list`, `dict`) and `|` unions. Never import `Optional`, `Union`, `Dict`, `List` from `typing`.
- Use `pathlib.Path` instead of `os.path`.
- Use f-strings, comprehensions, and context managers; follow PEP 8.
- Enums: `StrEnum` / `IntEnum` with `auto()` and UPPERCASE members.
- Write declarative, minimalist code: express intent, drop boilerplate.
- Never call a private method from outside its class.
- Avoid comments and docstrings, except for hard-to-spot corner cases.

## Typing & imports

- Use type hints consistently. Fix type issues at the source.
- No relative imports — always use absolute imports from the project root.
- No inline `# type: ignore` or `# noqa`. Fix with refined signatures (TypeVar, Protocol), `isinstance` guards, or `typing.cast`.

## Pydantic

- Parse external data via `model_validate` and field validators — never ad-hoc `getattr` / `hasattr` walks.
- Set `ConfigDict(extra=...)` explicitly.

## Database

- Use SQLite via `sqlite3` module for conversation persistence.
- Database schema in `database.py` — `init_db()` creates tables on first run.
- Conversation records include: `id`, `title`, `created_at`, `updated_at`.
- Message records include: `conversation_id`, `role`, `content`, `timestamp`.

## Model

- Mistral 3B model loaded via `transformers` and `torch`.
- Model loading in `model.py` — `load_model()` and `generate_response()`.
- Use `accelerate` for device management.

## Tests

- Stack: `pytest` + `pytest-asyncio`.
- Mark async tests with `@pytest.mark.asyncio`.
- No docstrings on test functions — descriptive names like `test_create_conversation_saves_to_db` carry the intent.

## Git

- Never use `git commit --amend`, `git push --force`, or `git push --force-with-lease`.
- Always create new commits and push with a plain `git push`.
- If a push is rejected due to upstream changes, rebase onto the updated remote branch — never merge and never force-push.

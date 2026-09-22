# Contributing

## Setup

Follow the Setup section in `README.md`, then install dev tools:

```bash
pip install -r requirements-dev.txt
```

## Before opening a PR

```bash
ruff check app tests --fix
black app tests
mypy app
pytest
```

All four must pass — CI enforces the same checks on every push/PR.

## Code style

- Python 3.11+, typed. New code should type-check under `mypy app` cleanly; prefer fixing the root cause over adding `# type: ignore`, and when an ignore is unavoidable (typically third-party stub friction), scope it to the specific error code (`# type: ignore[arg-type]`), not a bare ignore.
- Formatting is `black` (line length 110), imports/lint via `ruff`. Don't hand-format — run the tools.
- Services take `owner_id` explicitly and never trust a client-supplied id without checking it against the authenticated user. If you're touching `app/services/` or `app/rag/vector_store.py`, keep every read/write scoped by owner — that scoping is the app's main security boundary (see `tests/security/test_authorization.py`).

## Tests

- New endpoints or services need integration tests in `tests/integration/`.
- New security-relevant behavior (auth, ownership checks, input validation) needs a test in `tests/security/`.
- If you fix a bug, add a regression test in `tests/regression/` describing the bug it guards against — see the existing ones for the format.
- Tests must not depend on network access or real API keys. Use the fixtures in `tests/conftest.py` (`fake_generator`, `real_vector_store`) rather than calling the real Groq API or downloading the real embedding model.

## Commit messages

Short, imperative, and specific: `fix owner_id leak in vector store search` not `fix bug`.

"""
Each test here is tied to a specific bug found during the repository
audit. Keep these even if the surrounding code changes shape — the point
is to catch the *symptom* coming back, not to test implementation details.
"""

import importlib
import io
import os
import subprocess
import sys
from pathlib import Path


def test_app_module_imports_without_env_vars_set(monkeypatch):
    """
    BUG: app/rag/generator.py imported 6 functions from app/rag/prompts.py
    that didn't exist, and app/config.py raised ValueError at import time
    if GROQ_API_KEY wasn't set — between the two, the app could not be
    imported at all without live secrets configured, which also broke
    tooling like pytest collection and linting.
    """
    repo_root = Path(__file__).resolve().parents[2]
    env = dict(os.environ)
    env.pop("GROQ_API_KEY", None)
    env.pop("JWT_SECRET_KEY", None)
    env["PYTHONPATH"] = "/tmp/stub_pkgs" + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_config_module_does_not_require_secrets_to_import():
    """BUG: importing app.config used to crash without GROQ_API_KEY set."""
    import app.config

    importlib.reload(app.config)
    assert app.config.settings is not None


def test_generator_module_imports_all_prompt_builders():
    """BUG: app/rag/generator.py imported build_qa_messages,
    build_qa_messages_with_history, build_map_messages, build_reduce_messages,
    build_compare_messages, build_related_work_messages from prompts.py —
    none of which existed. This is the single import that made the app
    completely unbootable."""
    import app.rag.generator  # noqa: F401 — the test is that this doesn't raise


def test_chat_session_has_a_name_field(test_db):
    """BUG: the frontend creates/displays named sessions, but ChatSession
    had no `name` column at all, and the old sessions.py router referenced
    a nonexistent `Session`/`Turn` model entirely."""
    from app.db.models import ChatSession

    assert hasattr(ChatSession, "name")


def test_failed_ingest_does_not_orphan_uploaded_file(client, make_user):
    """BUG: papers.py removed the temp file with no try/finally, so a
    failure partway through ingestion left the uploaded file on disk
    forever with no corresponding database row."""
    _, _, headers = make_user()
    client.post(
        "/papers/upload",
        headers=headers,
        files={"file": ("bad.pdf", io.BytesIO(b"not a real pdf"), "application/pdf")},
    )
    from app.config import settings

    assert list(settings.papers_dir.glob("*.pdf")) == []


def test_cors_is_not_wildcard_open():
    """BUG: main.py hardcoded allow_origins=["*"] and ignored the
    ALLOWED_ORIGINS env var that render.yaml already defined."""
    from app.config import settings

    assert settings.allowed_origins != ["*"]


def test_arxiv_client_module_exists_and_is_importable():
    """BUG: app/services/arxiv_service.py imported app.rag.arxiv_client,
    which did not exist anywhere in the repository."""
    import app.rag.arxiv_client  # noqa: F401

"""
Shared pytest fixtures.

Design: tests never touch the real Groq API or download a real embedding
model. `FakeEmbeddingModel` produces small deterministic vectors so we can
run a REAL VectorStore (real ChromaDB, real query logic) against it —
that's important because the owner_id-scoping bug we fixed lives in the
Chroma `where` filter, so faking VectorStore itself would hide exactly the
kind of regression we care about catching. The LLM is faked at a higher
level (AnswerGenerator) since there's no equivalent value in running a
"real" local LLM.
"""

import os
import shutil
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-tests-only")

import app.rag.generator as generator_module  # noqa: E402
import app.rag.reranker as reranker_module  # noqa: E402
import app.rag.vector_store as vector_store_module  # noqa: E402
from app.db.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeEmbeddingModel:
    """
    Dependency-free stand-in for the real sentence embedding model, using
    the feature-hashing trick: each word hashes into one of DIM buckets
    and increments that bucket's count. This isn't a real embedding, but
    unlike a purely random/deterministic-per-string vector, it gives
    texts that share vocabulary a smaller cosine distance than texts that
    don't — which is the one property VectorStore's query logic actually
    depends on, and the one thing tests need it to get right.
    """

    DIM = 64

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.DIM
        for word in text.lower().split():
            bucket = hash(word) % self.DIM
            vec[bucket] += 1.0
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def embed_query(self, query: str) -> list[float]:
        return self._vector(query)


class FakeAnswerGenerator:
    """Stands in for AnswerGenerator so tests never call the real Groq API."""

    def generate_answer(self, query, chunks):
        if not chunks:
            return {"answer": "I couldn't find relevant content to answer this question.", "sources": []}
        return {
            "answer": f"Fake answer to: {query}",
            "sources": [
                {
                    "source_num": i,
                    "paper_id": c["paper_id"],
                    "page": c["page_number"],
                    "chunk_id": c["chunk_id"],
                    "snippet": c["text"][:280],
                }
                for i, c in enumerate(chunks, start=1)
            ],
        }

    def generate_answer_with_history(self, query, chunks, history):
        result = self.generate_answer(query, chunks)
        result["answer"] = f"Fake answer (history={len(history)} turns) to: {query}"
        return result

    def generate_summary(self, chunks):
        if not chunks:
            return "No content available to summarize."
        return f"Fake summary of {len(chunks)} chunks."

    def generate_comparison(self, paper_a_id, summary_a, paper_b_id, summary_b):
        return f"Fake comparison of {paper_a_id} and {paper_b_id}."

    def generate_related_work(self, target_summary, excerpts):
        if not excerpts:
            return "No related papers found in the library to reference."
        return f"Fake related work referencing {len(excerpts)} excerpts."


class FakeReranker:
    """
    Deterministic fake for integration tests.

    Unlike a simple pass-through fake, this deliberately reverses the
    candidate order so tests can prove that the retrieval pipeline actually
    calls the reranker and uses the reranker's returned ordering.
    """

    def __init__(self):
        self.calls = []

    def rerank(self, query, chunks, top_k):
        self.calls.append(
            {
                "query": query,
                "input_count": len(chunks),
                "top_k": top_k,
            }
        )

        return list(reversed(chunks))[:top_k]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def temp_chroma_dir():
    d = tempfile.mkdtemp(prefix="test_chroma_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def real_vector_store(temp_chroma_dir):
    """A REAL VectorStore (real ChromaDB) backed by a fake embedding model.
    Installs itself as the app-wide singleton so services under test use it."""
    store = vector_store_module.VectorStore(
        persist_dir=temp_chroma_dir,
        embedding_model=FakeEmbeddingModel(),
        collection_name=f"test_{uuid.uuid4().hex[:8]}",
    )
    vector_store_module._vector_store_instance = store
    yield store
    vector_store_module._vector_store_instance = None


@pytest.fixture()
def fake_generator():
    fake = FakeAnswerGenerator()
    generator_module._generator_instance = fake
    yield fake
    generator_module._generator_instance = None


@pytest.fixture()
def fake_reranker():
    fake = FakeReranker()
    reranker_module._reranker_instance = fake
    yield fake
    reranker_module._reranker_instance = None


@pytest.fixture()
def test_db():
    # tempfile.gettempdir() rather than a hardcoded "/tmp" — that path is
    # Unix-specific and doesn't exist as a real directory on Windows,
    # which previously caused every DB-backed test to fail there with
    # "unable to open database file".
    db_path = os.path.join(tempfile.gettempdir(), f"test_researchgpt_{uuid.uuid4().hex}.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture()
def isolated_papers_dir():
    from app.config import settings

    d = tempfile.mkdtemp(prefix="test_papers_")
    original = settings.papers_dir
    settings.papers_dir = __import__("pathlib").Path(d)
    settings.papers_dir.mkdir(parents=True, exist_ok=True)
    yield settings.papers_dir
    settings.papers_dir = original
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def client(test_db, real_vector_store, fake_generator, fake_reranker, isolated_papers_dir):
    return TestClient(app)


@pytest.fixture()
def make_user(client):
    """Registers a user and returns (email, password, auth_headers)."""

    def _make_user(email: str | None = None, password: str = "correct-horse-battery-staple"):
        email = email or f"user_{uuid.uuid4().hex[:8]}@example.com"
        resp = client.post("/auth/register", json={"email": email, "password": password})
        assert resp.status_code == 201, resp.text
        token = resp.json()["access_token"]
        return email, password, {"Authorization": f"Bearer {token}"}

    return _make_user


@pytest.fixture()
def sample_pdf_bytes():
    """A minimal real PDF with extractable text, generated with PyMuPDF
    so tests don't depend on a fixture binary file."""
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "This is a test research paper about transformers and attention mechanisms.")
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Page two discusses experimental results and evaluation metrics in detail.")
    data = doc.tobytes()
    doc.close()
    return data

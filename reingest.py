# reingest.py — run once, then delete
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

# Override the SAME "config" module ingest_service.py imports
# (must be plain "import config", not "app.config" — otherwise it's a
# different module object and the override silently does nothing)
import config
config.CHROMA_PATH = "chroma_db_test"
config.EMBEDDING_MODEL = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"

from app.services.ingest_service import ingest_pdf

ingest_pdf("data/tranformer for language understanfingv2.pdf", "tranformer for language understanfingv2")
ingest_pdf("data/NIPS-2017-attention-is-all-you-need-Paper.pdf", "NIPS-2017-attention-is-all-you-need-Paper")
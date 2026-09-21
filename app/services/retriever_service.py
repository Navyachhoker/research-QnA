from typing import List, Dict, Optional
from app.rag.vector_store import get_vector_store


def retrieve_chunks(query: str, top_k: int = 5, paper_id: Optional[str] = None) -> List[Dict]:
    return get_vector_store().search(query=query, top_k=top_k, paper_id=paper_id)
from typing import List, Dict
from app.rag.generator import get_generator


def answer_query(query: str, chunks: List[Dict]) -> Dict:
    return get_generator().generate_answer(query, chunks)


def answer_query_with_history(query: str, chunks: List[Dict], history: List[Dict]) -> Dict:
    return get_generator().generate_answer_with_history(query, chunks, history)
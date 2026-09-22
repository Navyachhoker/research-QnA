from app.rag.generator import get_generator


def answer_query(query: str, chunks: list[dict]) -> dict:
    return get_generator().generate_answer(query, chunks)


def answer_query_with_history(query: str, chunks: list[dict], history: list[dict]) -> dict:
    return get_generator().generate_answer_with_history(query, chunks, history)

import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
from fastapi import HTTPException

from app.rag.prompts import (
    build_qa_messages,
    build_qa_messages_with_history,
    build_map_messages,
    build_reduce_messages,
    build_compare_messages,
    build_related_work_messages,
)

load_dotenv()


class AnswerGenerator:
    """
    Wraps all Groq LLM calls. Takes the API key and model as constructor
    arguments (not read from env internally) so tests can inject a fake
    client instead of hitting the real Groq API.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self._client = Groq(api_key=api_key)
        self._model = model

    def _call(self, messages: List[Dict], temperature: float = 0.2) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
            )
        except Exception as exc:
            # Groq being down/rate-limited shouldn't crash with a raw 500 —
            # surface it as a clear upstream error instead.
            raise HTTPException(status_code=502, detail=f"LLM provider error: {exc}") from exc

        return response.choices[0].message.content

    def generate_answer(self, query: str, chunks: List[Dict]) -> Dict:
        if not chunks:
            return {"answer": "I couldn't find relevant content to answer this question.", "sources": []}

        answer_text = self._call(build_qa_messages(query, chunks))
        sources = [{"page_number": c["page_number"], "chunk_id": c["chunk_id"]} for c in chunks]
        return {"answer": answer_text, "sources": sources}

    def generate_answer_with_history(self, query: str, chunks: List[Dict], history: List[Dict]) -> Dict:
        if not chunks:
            return {"answer": "I couldn't find relevant content to answer this question.", "sources": []}

        answer_text = self._call(build_qa_messages_with_history(query, chunks, history))
        sources = [{"page_number": c["page_number"], "chunk_id": c["chunk_id"]} for c in chunks]
        return {"answer": answer_text, "sources": sources}

    def _batch_chunks(self, chunks: List[Dict], max_chars_per_batch: int = 6000) -> List[str]:
        batches = []
        current_batch = []
        current_length = 0

        for chunk in chunks:
            chunk_len = len(chunk["text"])
            if current_length + chunk_len > max_chars_per_batch and current_batch:
                batches.append("\n\n".join(current_batch))
                current_batch = []
                current_length = 0
            current_batch.append(chunk["text"])
            current_length += chunk_len

        if current_batch:
            batches.append("\n\n".join(current_batch))

        return batches

    def generate_summary(self, chunks: List[Dict]) -> str:
        if not chunks:
            return "No content available to summarize."

        batches = self._batch_chunks(chunks)
        section_summaries = [self._call(build_map_messages(b)) for b in batches]

        if len(section_summaries) == 1:
            return section_summaries[0]

        return self._call(build_reduce_messages(section_summaries))

    def generate_comparison(self, paper_a_id: str, summary_a: str, paper_b_id: str, summary_b: str) -> str:
        return self._call(build_compare_messages(paper_a_id, summary_a, paper_b_id, summary_b))

    def generate_related_work(self, target_summary: str, excerpts: List[Dict]) -> str:
        if not excerpts:
            return "No related papers found in the library to reference."
        return self._call(build_related_work_messages(target_summary, excerpts))


_generator_instance: "AnswerGenerator | None" = None


def get_generator() -> AnswerGenerator:
    global _generator_instance
    if _generator_instance is None:
        from app.config import settings
        _generator_instance = AnswerGenerator(
            api_key=settings.groq_api_key,
            model=settings.groq_model,   # <-- make sure this line is here
        )
    return _generator_instance
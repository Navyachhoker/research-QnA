from dotenv import load_dotenv
from fastapi import HTTPException
from groq import Groq

from app.rag.prompts import (
    build_compare_messages,
    build_map_messages,
    build_qa_messages,
    build_qa_messages_with_history,
    build_reduce_messages,
    build_related_work_messages,
)

load_dotenv()


class AnswerGenerator:
    """
    Wraps all Groq LLM calls. Takes the API key and model as constructor
    arguments (not read from env internally) so tests can inject a fake
    client instead of hitting the real Groq API.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-oss-120b",
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ):
        self._client = Groq(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def _call(self, messages: list[dict]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
        except Exception as exc:
            # Groq being down/rate-limited shouldn't crash with a raw 500 —
            # surface it as a clear upstream error instead.
            raise HTTPException(status_code=502, detail=f"LLM provider error: {exc}") from exc

        content = response.choices[0].message.content
        if content is None:
            raise HTTPException(status_code=502, detail="LLM provider returned an empty response.")
        return content

    def generate_answer(self, query: str, chunks: list[dict]) -> dict:
        if not chunks:
            return {"answer": "I couldn't find relevant content to answer this question.", "sources": []}

        answer_text = self._call(build_qa_messages(query, chunks))
        return {"answer": answer_text, "sources": self._format_sources(chunks)}

    def generate_answer_with_history(self, query: str, chunks: list[dict], history: list[dict]) -> dict:
        if not chunks:
            return {"answer": "I couldn't find relevant content to answer this question.", "sources": []}

        answer_text = self._call(build_qa_messages_with_history(query, chunks, history))
        return {"answer": answer_text, "sources": self._format_sources(chunks)}

    @staticmethod
    def _format_sources(chunks: list[dict]) -> list[dict]:
        return [
            {
                "source_num": i,
                "paper_id": c["paper_id"],
                "page": c["page_number"],
                "chunk_id": c["chunk_id"],
                "snippet": (c["text"][:280] + "…") if len(c["text"]) > 280 else c["text"],
            }
            for i, c in enumerate(chunks, start=1)
        ]

    def _batch_chunks(self, chunks: list[dict], max_chars_per_batch: int = 6000) -> list[str]:
        batches: list[str] = []
        current_batch: list[str] = []
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

    def generate_summary(self, chunks: list[dict]) -> str:
        if not chunks:
            return "No content available to summarize."

        batches = self._batch_chunks(chunks)
        section_summaries = [self._call(build_map_messages(b)) for b in batches]

        if len(section_summaries) == 1:
            return section_summaries[0]

        return self._call(build_reduce_messages(section_summaries))

    def generate_comparison(self, paper_a_id: str, summary_a: str, paper_b_id: str, summary_b: str) -> str:
        return self._call(build_compare_messages(paper_a_id, summary_a, paper_b_id, summary_b))

    def generate_related_work(self, target_summary: str, excerpts: list[dict]) -> str:
        if not excerpts:
            return "No related papers found in the library to reference."
        return self._call(build_related_work_messages(target_summary, excerpts))


_generator_instance: "AnswerGenerator | None" = None


def get_generator() -> AnswerGenerator:
    global _generator_instance
    if _generator_instance is None:
        from app.config import settings

        _generator_instance = AnswerGenerator(
            api_key=settings.require_groq_api_key(),
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
    return _generator_instance

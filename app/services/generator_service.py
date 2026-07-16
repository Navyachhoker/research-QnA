# app/rag/generator.py

from groq import Groq

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)

client = Groq(api_key=GROQ_API_KEY)


def generate(
    question: str,
    chunks: list[dict],
    history: list[dict] | None = None,
) -> dict:
    """
    Generate an answer using:
    - Retrieved RAG chunks
    - Conversation history
    """

    if not chunks:
        return {
            "answer": "No relevant content found.",
            "sources": [],
        }

    if history is None:
        history = []

    prompt = _build_prompt(
        question=question,
        chunks=chunks,
        history=history,
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI research assistant. "
                    "Answer only using the supplied context. "
                    "If the answer cannot be found, say so."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    answer = response.choices[0].message.content.strip()

    sources = [
        {
            "source_num": i,
            "paper": chunk["paper"],
            "page": chunk["page"],
            "snippet": chunk["text"][:200] + "...",
        }
        for i, chunk in enumerate(chunks, start=1)
    ]

    return {
        "answer": answer,
        "sources": sources,
    }


def _build_prompt(question: str, chunks: list[dict], history: list[dict]) -> str:
    context = "\n\n".join(
        f"[Source {i}]\nPaper: {c['paper']} | Page: {c['page']}\n---\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    )

    history_str = ""
    if history:
        history_str = "CONVERSATION HISTORY:\n"
        for turn in history:
            history_str += f"\nUser: {turn['question']}\nAssistant: {turn['answer']}\n"
        history_str += "\n---\n"

    return f"""You are an expert research paper analyst. Answer questions about academic papers clearly and precisely.

RULES:
1. Answer ONLY using the provided context — never use outside knowledge
2. Cite every claim with [Source N] immediately after the sentence
3. Use clear academic language but keep it accessible
4. Structure longer answers with bullet points or numbered lists
5. If comparing papers, clearly label which paper you're referring to
6. If the answer isn't in the context say: "This information is not available in the provided papers."

CONTEXT FROM PAPERS:
{context}

{history_str}
QUESTION: {question}

ANSWER:"""
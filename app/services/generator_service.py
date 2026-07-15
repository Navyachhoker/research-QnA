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


def _build_prompt(
    question: str,
    chunks: list[dict],
    history: list[dict],
) -> str:
    """
    Builds the complete prompt using:
      • Retrieved paper chunks
      • Conversation history
      • Current question
    """

    context = "\n\n".join(
        f"[Source {i}]\n"
        f"Paper: {chunk['paper']}\n"
        f"Page: {chunk['page']}\n\n"
        f"{chunk['text']}"
        for i, chunk in enumerate(chunks, start=1)
    )

    history_text = ""

    if history:
        history_text = (
            "Conversation History "
            "(Use only for context. Do not repeat previous answers.)\n\n"
        )

        for turn in history:
            history_text += (
                f"User: {turn['question']}\n"
                f"Assistant: {turn['answer']}\n\n"
            )

    return f"""
You are an expert research assistant helping users understand research papers.

Instructions:
- Use the provided paper context to answer the question.
- Combine information from multiple sources when needed.
- Summarize and explain concepts clearly.
- Do NOT copy large passages verbatim.
- Cite supporting sources as [Source X].
- Only say "I could not find a relevant answer in the provided papers."
  if the provided context contains no information relevant to the question.

==========================
PAPER CONTEXT
==========================

{context}

==========================
{history_text}
==========================

Question:
{question}

Answer:
"""
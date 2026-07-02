from groq import Groq

from app.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)

from app.rag.prompts import build_rag_prompt

client = Groq(api_key=GROQ_API_KEY)

prompt = build_rag_prompt(question, chunks)


def generate(
    question: str,
    chunks: list[dict],
) -> dict:
    """
    Generate the final answer using the retrieved chunks.

    Steps:

    User Question
            ↓
    Retrieved Chunks
            ↓
    Prompt Construction
            ↓
    Groq LLM
            ↓
    Final Answer + Sources
    """

    # -------------------------------------------------
    # If nothing was retrieved, there is no context
    # available for the LLM.
    # -------------------------------------------------

    if not chunks:
        return {
            "answer": "No relevant content found.",
            "sources": [],
        }

    # Build the complete prompt.
    prompt = build_prompt(
        question,
        chunks,
    )

    # -------------------------------------------------
    # Send the prompt to Groq's language model.
    # -------------------------------------------------

    response = client.chat.completions.create(
        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": "You are a helpful research assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    # -------------------------------------------------
    # Prepare source information.
    #
    # This allows the frontend to display where the
    # answer came from.
    # -------------------------------------------------

    sources = []

    for i, chunk in enumerate(chunks, start=1):

        sources.append(
            {
                "source_num": i,
                "paper": chunk["paper"],
                "page": chunk["page"],

                # Store only a short preview instead of
                # the entire chunk.
                "snippet": chunk["text"][:200] + "...",
            }
        )

    # -------------------------------------------------
    # Return the generated answer and source details.
    # -------------------------------------------------

    return {
        "answer": response.choices[0].message.content.strip(),
        "sources": sources,
    }
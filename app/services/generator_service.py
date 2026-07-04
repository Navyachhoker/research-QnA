from groq import Groq

from app.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)

from app.rag.prompts import build_rag_prompt

client = Groq(api_key=GROQ_API_KEY)



def generate(
    question: str,
    chunks: list[dict],
) -> dict:
  

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
    prompt = build_rag_prompt(
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
    
    
def _build_prompt(question: str, chunks: list[dict], history: list[dict]) -> str:
    """
    Build the full prompt including:
      1. Retrieved context chunks (RAG)
      2. Past conversation turns (memory)
      3. Current question
    """
    context = "\n\n".join(
        f"[Source {i}]\nPaper: {c['paper']} | Page: {c['page']}\n---\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    )

    # Format past turns so the LLM understands the conversation so far
    history_str = ""
    if history:
        history_str = "CONVERSATION HISTORY (for context only — do not re-answer these):\n"
        for turn in history:
            history_str += f"\nUser: {turn['question']}\nAssistant: {turn['answer']}\n"
        history_str += "\n---\n"

    return f"""You are a research assistant. Answer using ONLY the provided context.
After every key claim, cite with [Source N].
If the answer isn't in the context, say: "I could not find a relevant answer."

CONTEXT FROM PAPERS:
{context}

{history_str}
CURRENT QUESTION:
{question}

ANSWER:"""

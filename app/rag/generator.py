#Uses Groq LLM to generate answers from retrieved document chunks.


import os

from dotenv import load_dotenv
from groq import Groq

from app.config import (
    GROQ_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)

from app.rag.prompts import build_rag_prompt

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(
    question: str,
    chunks: list[dict],
):
    """
    Generate answer using retrieved chunks.
    """

    if not chunks:

        return {
            "answer": "No relevant information found.",
            "sources": [],
        }

    prompt = build_rag_prompt(
        question,
        chunks,
    )

    response = client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content":
                "You answer only using the supplied context.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        temperature=TEMPERATURE,

        max_tokens=MAX_TOKENS,
    )

    answer = response.choices[0].message.content

    sources = []

    for index, chunk in enumerate(chunks, start=1):

        sources.append(
            {
                "source_num": index,
                "paper": chunk["paper"],
                "page": chunk["page"],
                "snippet": chunk["text"][:200] + "...",
            }
        )

    return {

        "answer": answer,

        "sources": sources,
    }
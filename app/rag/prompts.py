# Prompt templates used by the LLM.

def build_rag_prompt(
    question: str,
    chunks: list[dict],
) -> str:
    """
    Build a prompt using retrieved chunks.
    """

    context = []

    for i, chunk in enumerate(chunks, start=1):

        context.append(
            f"""
[Source {i}]
Paper: {chunk['paper']}
Page: {chunk['page']}

{chunk['text']}
"""
        )

    context = "\n\n".join(context)

    prompt = f"""
You are an AI Research Assistant.

Answer ONLY using the supplied context.

Context

{context}

Question

{question}

Instructions

1. Answer only from the supplied context.
2. Cite every important statement using [Source X].
3. If the answer isn't in the context, reply:

"I could not find a relevant answer in the provided papers."

Answer:
"""

    return prompt
# Prompt templates used by the LLM.


#is responsilbe for creating the final prompt 
# that is sent to LLM
#includes  q from user,
#retrived doc chunk
#clear instructions for the model
def build_rag_prompt(
    question: str,
    chunks: list[dict],
) -> str:

    # Build a prompt using retrieved chunks

    # will store the formatted chunks
    context = []

    for i, chunk in enumerate(chunks, start=1):
        #fromats each chunk into readable block
        context.append(
            f"""
[Source {i}]
Paper: {chunk['paper']} 
Page: {chunk['page']}

{chunk['text']}
"""
        )

    #joining all the chunks into 1 long string
    context = "\n\n".join(context)



    # creating the compelete prompt
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
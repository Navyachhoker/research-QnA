"""
Uses your existing Groq wiring to score whether the generated answer is:
- Faithful: grounded in the retrieved context (not hallucinated)
- Relevant: actually answers the question asked

Why LLM-as-judge instead of exact string match: RAG answers are free text,
there's no single "correct" phrasing. A judge model can evaluate meaning,
not just string overlap.
"""

import json
from groq import Groq  # you already have this in your TEOCO stack

client = Groq()  # assumes GROQ_API_KEY is set in env

JUDGE_PROMPT = """You are evaluating a RAG system's answer. Score strictly.

Question: {question}
Retrieved Context: {context}
Generated Answer: {answer}

Score on two dimensions, 1-5 each:
1. FAITHFULNESS: Is every claim in the answer supported by the context?
   (5 = fully grounded, 1 = mostly fabricated / not in context)
2. RELEVANCE: Does the answer actually address the question asked?
   (5 = directly answers it, 1 = off-topic or evasive)

Respond ONLY with valid JSON, no other text:
{{"faithfulness": <int>, "relevance": <int>, "reasoning": "<one sentence>"}}
"""

def judge_answer(question: str, context: str, answer: str) -> dict:
    prompt = JUDGE_PROMPT.format(question=question, context=context, answer=answer)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # deterministic scoring, not creative
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # judge sometimes wraps in markdown fences — strip and retry once
        cleaned = raw.strip("`").replace("json\n", "")
        return json.loads(cleaned)
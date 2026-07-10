#summarization + comparison logic

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL,TEMPERATURE, MAX_TOKENS
from services.retriever_service import retrieve
from services.ingest_service import list_papers

client = Groq(api_key = GROQ_API_KEY)

def _call_groq(system_prompt: str, user_prompt: str)-> str:
    response = client.chat.completions.create(
        model = GROQ_MODEL,
        messages =[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    
    return response.choices[0].message.content.strip()

#summarize_paper

def summarize_paper(paper_name: str)-> dict:
    if paper_name not in list_papers():
        raise ValueError(f"Paper '{paper_name}' not found in the knowledge base.")

    # Pull diverse chunks covering different aspects of the paper
    aspect_queries = [
        "main contribution and problem statement",
        "methodology and approach",
        "experiments results and evaluation",
        "conclusion and future work",
    ]

    seen_chunks = {}
    for query in aspect_queries:
        chunks = retrieve(query, top_k=3, paper=paper_name)
        for c in chunks:
            # Deduplicate by chunk_index to avoid repeating the same chunk
            key = (c["paper"], c["page"], c["chunk_index"])
            if key not in seen_chunks:
                seen_chunks[key] = c

    all_chunks = list(seen_chunks.values())

    context = "\n\n".join(
        f"[Page {c['page']}]\n{c['text']}"
        for c in all_chunks
    )

    system = "You are an expert research assistant that summarizes academic papers clearly and accurately."

    user = f"""Summarize the following research paper excerpts into a structured summary.

PAPER: {paper_name}

EXCERPTS:
{context}

Write the summary using this exact structure:

## Overview
(1-2 sentences: what problem does the paper solve and why does it matter)

## Key Contributions
(bullet points of the main contributions)

## Methodology
(how the authors approach the problem)

## Results
(main findings and metrics if available)

## Limitations & Future Work
(what the authors acknowledge as limitations or future directions)

Base everything strictly on the excerpts provided."""

    summary = _call_groq(system, user)

    return {
        "paper":      paper_name,
        "summary":    summary,
        "chunk_count": len(all_chunks),
    }
    
    # ── Comparison ─────────────────────────────────────────────────────────────────

def compare_papers(paper_a: str, paper_b: str) -> dict:
    """
    Compare two papers across key dimensions.

    Strategy:
      - For each comparison dimension, retrieve relevant chunks from BOTH papers
      - Send all chunks together so the LLM can directly contrast them
    """
    all_papers = list_papers()
    for name in [paper_a, paper_b]:
        if name not in all_papers:
            raise ValueError(f"Paper '{name}' not found in the knowledge base.")

    # Dimensions we want to compare across
    comparison_queries = [
        "problem statement and motivation",
        "proposed method and approach",
        "evaluation and results",
        "limitations and future work",
    ]

    chunks_a, chunks_b = [], []
    seen_a, seen_b = set(), set()

    for query in comparison_queries:
        for chunk in retrieve(query, top_k=3, paper=paper_a):
            key = (chunk["page"], chunk["chunk_index"])
            if key not in seen_a:
                chunks_a.append(chunk)
                seen_a.add(key)

        for chunk in retrieve(query, top_k=3, paper=paper_b):
            key = (chunk["page"], chunk["chunk_index"])
            if key not in seen_b:
                chunks_b.append(chunk)
                seen_b.add(key)

    context_a = "\n\n".join(f"[Page {c['page']}]\n{c['text']}" for c in chunks_a)
    context_b = "\n\n".join(f"[Page {c['page']}]\n{c['text']}" for c in chunks_b)

    system = "You are an expert research assistant that compares academic papers objectively."

    user = f"""Compare these two research papers based on the excerpts provided.

PAPER A: {paper_a}
{context_a}

---

PAPER B: {paper_b}
{context_b}

---

Write the comparison using this exact structure:

## Problem Being Solved
- **{paper_a}**: ...
- **{paper_b}**: ...

## Methodology
- **{paper_a}**: ...
- **{paper_b}**: ...

## Results & Performance
- **{paper_a}**: ...
- **{paper_b}**: ...

## Strengths
- **{paper_a}**: ...
- **{paper_b}**: ...

## Weaknesses / Limitations
- **{paper_a}**: ...
- **{paper_b}**: ...

## Which to Use When
(practical guidance: when would you choose one over the other)

Base everything strictly on the provided excerpts. Do not use outside knowledge."""

    comparison = _call_groq(system, user)

    return {
        "paper_a":     paper_a,
        "paper_b":     paper_b,
        "comparison":  comparison,
        "chunks_used": {"paper_a": len(chunks_a), "paper_b": len(chunks_b)},
    }


# ── Related Work Generator 

def generate_related_work(topic: str) -> dict:
    """
    Generate a 'Related Work' section by pulling relevant chunks
    from ALL ingested papers and synthesizing them into academic prose.
    """
    papers = list_papers()
    if not papers:
        raise ValueError("No papers ingested yet.")

    all_chunks = []
    seen = set()

    for paper in papers:
        chunks = retrieve(topic, top_k=3, paper=paper)
        for c in chunks:
            key = (c["paper"], c["page"], c["chunk_index"])
            if key not in seen:
                all_chunks.append(c)
                seen.add(key)

    context = "\n\n".join(
        f"[{c['paper']} | Page {c['page']}]\n{c['text']}"
        for c in all_chunks
    )

    system = "You are an expert academic writer skilled at writing Related Work sections for research papers."

    user = f"""Write a 'Related Work' section for a paper about: "{topic}"

Use ONLY the following excerpts from the papers listed:

{context}

Requirements:
- Write in formal academic prose (3-5 paragraphs)
- Group related ideas together thematically, not paper by paper
- Cite papers inline like (Paper Name, Year) where year is unknown use (Paper Name)
- Highlight how the papers relate to each other and to the topic
- End with a sentence explaining what gap the current work fills

Do not use any knowledge outside the provided excerpts."""

    related_work = _call_groq(system, user)

    return {
        "topic":        topic,
        "related_work": related_work,
        "papers_used":  papers,
        "chunks_used":  len(all_chunks),
    }

# Coordinates the ingestion pipeline

import os

from app.rag.embeddings import embedder

from app.rag.vector_store import (
    store_chunks,
)

from app.utils.pdf_utils import (
    extract_text_from_pdf,
    chunk_text,
)


def ingest_pdf(
    pdf_path: str,
) -> str:
    """
    Ingest a single PDF into ChromaDB.
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    paper_name = os.path.splitext(
        os.path.basename(pdf_path)
    )[0]

    print(f"\n[Ingest] Processing '{paper_name}'")

    pages = extract_text_from_pdf(pdf_path)

    chunks = chunk_text(pages)

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedder.encode(
        texts,
        show_progress_bar=True,
    ).tolist()

    ids = []

    documents = []

    metadatas = []

    for chunk in chunks:

        ids.append(
            f"{paper_name}_p{chunk['page']}_c{chunk['chunk_index']}"
        )

        documents.append(
            chunk["text"]
        )

        metadatas.append(
            {
                "paper": paper_name,
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
            }
        )

    store_chunks(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"[Ingest] Stored {len(chunks)} chunks.")

    return paper_name
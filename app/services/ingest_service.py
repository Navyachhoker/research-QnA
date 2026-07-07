import os
import fitz
import chromadb
from sentence_transformers import SentenceTransformer
from app.config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)

from app.utils.pdf_utils import (
    extract_text_from_pdf,
    chunk_text,
)

embedder = SentenceTransformer(EMBEDDING_MODEL)

chroma = chromadb.PersistentClient(
    path= CHROMA_PATH
)

collection = chroma.get_or_create_collection(
    name= COLLECTION_NAME
)

def ingest_pdf(pdf_path: str, paper_name: str) -> int:
    print("1. Starting ingestion")

    pages = extract_text_from_pdf(pdf_path)
    print("2. Text extracted")

    chunks = chunk_text(pages)
    print(f"3. Created {len(chunks)} chunks")

    texts = [chunk["text"] for chunk in chunks]
    print("4. Prepared text list")

    embeddings = embedder.encode(
        texts,
        show_progress_bar=True
    ).tolist()
    print("5. Embeddings generated")

    ids = [
        f"{paper_name}__p{chunk['page']}__c{chunk['chunk_index']}"
        for chunk in chunks
    ]
    print("6. IDs created")

    metadatas = [
        {
            "paper": paper_name,
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
        }
        for chunk in chunks
    ]
    print("7. Metadata created")

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    print("8. Stored in Chroma")

    return len(chunks)

def list_papers() -> list[str]:
    result = collection.get(
        include = ["metadatas"]
    )
    
    metadata = result["metadatas"]
    
    papers = sorted(
        {
            item["paper"]
            for item in metadata
        }
    )
    
    return papers
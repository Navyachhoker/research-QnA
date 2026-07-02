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

def ingest_pdf(
    pdf_path: str,
    paper_name: str,
) -> int:
    print("1. Starting ingestion")
    pages = extract_text_from_pdf(pdf_path)
    
    chunks = chunk_text(pages)
    
    #only get chunk text for embedding generation
    texts = [
        chunk["text"]
        for chunk in chunks
    ]
    
    #Generate vector embeddings
    embeddings = embedder.encode(
        texts,
        show_progress_bar=False
    ).tolist()
    
    # Create a unique ID for every chunk
    ids = [
        f"{paper_name}__p{chunk['page']}__c{chunk['chunk_index']}"
        for chunk in chunks
    ]
    
    # Store useful metadata with every chunk
    metadatas = [
        {
            "paper": paper_name,
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
        }
        for chunk in chunks
    ]

    # Store everything inside ChromaDB
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"[INGEST] Stored {len(chunks)} chunks for '{paper_name}'.")

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
import chroma_db

from app.config import(
    CHROMA_PATH,
    COLLECTION_NAME,
)

client = chroma_db.PresistentClient(
    path = CHROMA_PATH
)

collection = client.get_or_create_collection(
    name = COLLECTION_NAME
)

#store doc chunks and thier embedding in chromadb
def store_chunks(
    ids, 
    embeddings,
    documents,
    metadatas,
):

#upsert-> if not exist inert, if exists then updates
    collection.upsert(
        ids = ids, 
        embeddings= embeddings, 
        documents=documents,
        metadatas=metadatas,
    )
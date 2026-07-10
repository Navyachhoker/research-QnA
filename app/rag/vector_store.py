import chroma_db

from config import(
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
    collection.upsert(      #chromadb method
        ids = ids, 
        embeddings= embeddings, 
        documents=documents,
        metadatas=metadatas,
    )
    
# retrieve chunks
def query_chunks(
    query_embedding,
    top_k,
    where = None,
):
    #perform similarity search
    return collection.query(
        query_embeddings = query_embedding,
        n_results = top_k,
        where = where,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )
    
    
#list papers
def get_all_papers():
    data = collection.get(
        include = ["metadata"]
    )
    #set comprehension
    papers = {
        meta["paper"] #expression-> value added to the set
        for meta in data["metadata"] # meta(item)-> var representing each element
        #data(iterable)
    }
    
    return sorted(list(papers))


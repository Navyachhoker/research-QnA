#functions-> extract text from pdf pages
#split text into overlapping chunks


#module provided by pyMuPDF for working with pdfs
import fitz 
from config import(
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)




def extract_text_from_pdf(pdf_path:str)-> list[dict]:#retuns a list
    #extract text from every pg of a pdf
    document= fitz.open(pdf_path) #
    pages = [] #will store extracted pgs
    
    for page_number in range(len(document)):
        page = document[page_number]
        
        text = page.get_text("text").strip() 
        #extract all text from pg 
        #strip removes unnecessary blank lines , 
        # makes chunking cleaner, 
        # improves the quality of the text sent to the embedding model
        if text:
            pages.append(
                {
                    "page": page_number + 1,
                    "text": text,
                }
            )

    document.close()

    print(f"[PDF] Extracted {len(pages)} pages.")

    return pages






def chunk_text(
    pages: list[dict],
    chunk_size: int = CHUNK_SIZE, # = gives default value
    overlap: int = CHUNK_OVERLAP, 
) -> list[dict]:
    #Split extracted pages into overlapping chunks
    
    #will store all generated chunks
    chunks = []

    for page_data in pages:

        text = page_data["text"]

        page = page_data["page"]
        
        #starting position of the first chunk
        start = 0 

        chunk_index = 0 # chunk counter

        while start < len(text):
            # calculates where the current chunk should end
            end = start + chunk_size 
            # a dict representing 1 chunk is created 
            # and added to list(chunks)
            chunks.append(
                {
                    "page": page,
                    "chunk_index": chunk_index,
                    "text": text[start:end],
                }
            )
        # represents the starting position for next chunk
            start += chunk_size - overlap 

            #inc chunk no
            chunk_index += 1

    print(f"[PDF] Created {len(chunks)} chunks.")

    return chunks

        
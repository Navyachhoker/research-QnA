import fitz
from app.config import(
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def extract_text_from_pdf(pdf_path:str)-> list[dict]:
    #extract text from every pg of a pdf
    document= fitz.open(pdf_path)
    pages = []
    
    for page_number in range(len(document)):
        page = document[page_number]
        
        text = page.get_text("text").strip()
        
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
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Split extracted pages into overlapping chunks.
    """

    chunks = []

    for page_data in pages:

        text = page_data["text"]

        page = page_data["page"]

        start = 0

        chunk_index = 0

        while start < len(text):

            end = start + chunk_size

            chunks.append(
                {
                    "page": page,
                    "chunk_index": chunk_index,
                    "text": text[start:end],
                }
            )

            start += chunk_size - overlap

            chunk_index += 1

    print(f"[PDF] Created {len(chunks)} chunks.")

    return chunks

        
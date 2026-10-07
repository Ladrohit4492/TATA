from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_chunk_pdf(pdf_path):
    # Step 1: Load the PDF and extract its text, page by page
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages from the PDF.")

    # Step 2: Split the text into smaller chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,      # roughly how many characters per chunk
        chunk_overlap=100    # slight overlap so context isn't lost between chunks
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks.")

    return chunks

# This block only runs if you execute this file directly (for testing)
if __name__ == "__main__":
    pdf_path = "sample.pdf"  # we'll put a test PDF here shortly
    chunks = load_and_chunk_pdf(pdf_path)

    # Print the first chunk so we can see what it looks like
    print("\n--- Example chunk ---")
    print(chunks[0].page_content)
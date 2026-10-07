import os
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv
from ingest import load_and_chunk_pdf

# Load your API key from the .env file
load_dotenv()
#print("API KEY LOADED:", os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create a local, persistent vector database (saves to a folder called chroma_db)
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="hld_documents")

def embed_text(text, task_type="retrieval_document"):
    """Convert a piece of text into a numerical embedding using Gemini."""
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type=task_type
    )
    return result["embedding"]

def build_vector_store(pdf_path):
    """Read a PDF, chunk it, embed each chunk, and store it in ChromaDB."""
    chunks = load_and_chunk_pdf(pdf_path)

    # Clear old data so documents don't mix together
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)

    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk.page_content)
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding],
            documents=[chunk.page_content],
            metadatas=[{"page": chunk.metadata.get("page", "unknown")}]
        )
        print(f"Stored chunk {i+1}/{len(chunks)}")

    print("\nAll chunks embedded and stored.")

def search_similar_chunks(query, top_k=3):
    """Given a question, find the most relevant chunks from the vector store."""
    query_embedding = embed_text(query, task_type="retrieval_query")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results

if __name__ == "__main__":
    build_vector_store("sample.pdf")

    print("\n--- Testing search ---")
    test_query = "What is this document about?"
    results = search_similar_chunks(test_query)
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"\nPage {meta['page']}:")
        print(doc[:200], "...")
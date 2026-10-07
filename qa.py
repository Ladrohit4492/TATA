import os
import google.generativeai as genai
from dotenv import load_dotenv
from vectorstore import search_similar_chunks

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-3.6-flash")

def answer_question(question, top_k=3):
    """Retrieve relevant chunks and ask Gemini to answer using only that context."""
    results = search_similar_chunks(question, top_k=top_k)

    context_chunks = results["documents"][0]
    pages = [meta["page"] for meta in results["metadatas"][0]]

    context_text = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are an assistant answering questions about an AUTOSAR HLD document.
Use ONLY the context below to answer the question. If the answer is not in the context, say so clearly.
Do not make up information.

Context:
{context_text}

Question: {question}

Answer:"""

    response = model.generate_content(prompt)


    return {
        "answer": response.text,
        "source_pages": list(set(pages))
    }

if __name__ == "__main__":
    question = "What is the recommended vector database for this solution?"
    result = answer_question(question)

    print("Question:", question)
    print("\nAnswer:", result["answer"])
    print("\nSource pages:", result["source_pages"])
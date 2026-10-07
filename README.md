# CS1: AUTOSAR HLD Document Analysis Assistant

Tata Technologies Tech Pulse AI/ML Capstone, Case Study 1
**Student:** Rohit Lad | **PRN:** 123B1B176 | **Institute:** PCCOE, Pune

## Overview
A Retrieval-Augmented Generation (RAG) assistant that lets an engineer ask questions in plain language about an AUTOSAR High-Level Design (HLD) document. Answers come only from the document and include page citations so they can be checked.

The knowledge base is the Case Study 1 brief (`sample.pdf`), pre-loaded and indexed. Document upload is outside the scope of this pilot.

## How it works
1. **Ingest** (`ingest.py`): the PDF is read with PyPDFLoader (keeps page numbers) and split into chunks of 800 characters with 100 overlap.
2. **Index** (`vectorstore.py`): each chunk is embedded with `gemini-embedding-001` and stored in a local ChromaDB collection (`hld_documents`).
3. **Answer** (`qa.py`): the question is embedded, the top 3 similar chunks are retrieved, and `gemini-3.6-flash` answers using only that context. If the answer is not in the context, it says so.
4. **Interface** (`app.py`): a Streamlit page with a question box and a "Get Answer" button. It shows the answer and source pages.

Page numbers are 0-based (page 0 is the first page).

## Files
| File | Purpose |
|---|---|
| `ingest.py` | Load PDF and split into chunks |
| `vectorstore.py` | Create embeddings and build the ChromaDB index |
| `qa.py` | Retrieval and grounded answer generation |
| `app.py` | Streamlit user interface |
| `evaluate.py` | Runs test questions and saves results |
| `sample.pdf` | Knowledge base (Case Study 1 brief) |
| `requirements.txt` | Python dependencies |
| `docs/` | Report, synopsis, model/prompt config, test set and evaluation results |

## Setup (Windows)
Requires Python 3.12 and a Google Gemini API key.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a file named `.env` in the project folder containing:

```
GOOGLE_API_KEY=your_key_here
```

## Run
```
python vectorstore.py      # build the index (first time only)
streamlit run app.py       # opens http://localhost:8501
python evaluate.py         # run the evaluation
```

## Evaluation
`evaluate.py` runs 5 test questions plus 1 negative test ("What is the capital of France?") through the real pipeline. It saves `Evaluation_Results.csv` and `Evaluation_Results.md` with the answer, cited pages and response time. The keyword check is automatic, and answers are also reviewed manually.

## External API declaration
This project uses the Google Gemini API over the internet for embeddings and answer generation, so it is not fully local. Only the approved case-study text is sent. The vector index is stored locally. The reference document recommends locally hosted models (for example Llama or Mistral with BGE or E5 embeddings), and moving to these is the planned next step.

## Limitations and future work
- Does not extract structured items (components, interfaces, signals)
- Does not compare document versions
- Tested on one three-page document
- No Docker or experiment tracking
- Future: local LLM and embeddings, structured extraction, version comparison, more test documents

## AI assistance
Claude was used for coding help and debugging. The code has been reviewed by the author.

## Security note
Never commit `.env`. It holds the API key and is excluded by `.gitignore`.
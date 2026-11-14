# DocuMind AI — Document-based RAG Study Assistant

StudyMate AI lets a user create an account, upload study documents, and ask questions. It retrieves relevant text from the uploaded files and asks an LLM to answer only from that retrieved context.

## Features
- Login and account creation (local SQLite database)
- Upload PDF, DOCX, PPTX, TXT and Markdown files
- Select 2-mark, 5-mark, 10-mark or Bits (MCQ) answer format
- Text chunking with overlap
- OpenAI embeddings and cosine-similarity retrieval
- Grounded answers with source filename and chunk references

## Requirements
- Python 3.10 or later
- An OpenAI API key with API access and billing enabled

## Setup on Windows PowerShell

```powershell
# 1. Extract the ZIP and open the project folder
cd StudyMate_RAG_Project

# 2. Create a virtual environment
py -m venv .venv

# 3. Activate it
.\.venv\Scripts\Activate.ps1

# 4. Install packages
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Create your environment file
Copy-Item .env.example .env
```

Open `.env` and replace the example value with your own API key:

```text
OPENAI_API_KEY=your_real_key_here
```

Keep the key private. Do not upload `.env` to GitHub.

## Run

```powershell
streamlit run app.py
```

The browser opens the StudyMate dashboard. Create an account, log in, upload documents in the sidebar, click **Process documents**, choose an answer format, and ask a question.

## How RAG works in this project

1. **Load:** extract text from supported files.
2. **Chunk:** split the extracted text into 1,000-character chunks with 150-character overlap.
3. **Embed:** convert each chunk into a numerical vector using `text-embedding-3-small`.
4. **Store:** keep vectors, text and file metadata in the current Streamlit session.
5. **Retrieve:** embed the question and compare it with chunk vectors using cosine similarity. The top 5 chunks are selected.
6. **Generate:** send only the retrieved passages and the question to `gpt-4o-mini`. A strict prompt tells the model not to use outside knowledge.

## Important limitations
- Scanned/image-only PDFs need OCR. This starter version extracts selectable PDF text; it does not perform OCR.
- DOCX, PPTX, TXT and MD are supported. Other file formats need additional parsers.
- The index is held in the active browser session and is cleared when the session ends or the user logs out. It is not a permanent multi-user vector database.
- Login is a classroom-project starter, not production-grade authentication. For a real deployment, add HTTPS, rate limiting, email verification, password reset and stronger session management.
- Retrieval can miss relevant passages. Review the source chunks and tune chunk size, overlap and top_k for your documents.
- LLM output cannot be guaranteed perfect. The system is designed to reduce unsupported answers by grounding responses in retrieved text and explicitly admitting when context is insufficient.

## Project structure

```text
StudyMate_RAG_Project/
├── app.py                 # Streamlit login, dashboard and chat UI
├── database.py            # SQLite user accounts and password hashing
├── document_loader.py     # PDF/DOCX/PPTX/TXT/MD text extraction
├── chunking.py            # Text chunking with overlap
├── rag_engine.py          # Embeddings, retrieval and LLM answer generation
├── requirements.txt
├── .env.example
└── README.md
```

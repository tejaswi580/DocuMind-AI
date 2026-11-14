# DocuMind AI
### Answers Tailored to Your Marks

## About the Project

DocuMind AI is an AI-powered document-based study assistant developed using Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs).

It helps students prepare for examinations by uploading their study materials and generating answers based on the uploaded documents.

Students can select different answer formats:
- 2 Marks
- 5 Marks
- 10 Marks
- Bits (MCQs)

## Features

- User Registration and Login using SQLite
- Upload PDF, DOCX, PPTX, TXT and Markdown files
- Automatic text extraction
- Text chunking with overlap
- Embedding generation using Google Gemini
- Similarity search using cosine similarity
- Retrieval of the top 5 relevant chunks
- Marks-based answer generation
- MCQ generation
- Download document embeddings as CSV

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | User interface |
| Google Gemini API | Embedding and answer generation |
| Gemini Embedding Model | Converts text into numerical vectors |
| NumPy | Numerical operations and similarity calculation |
| SQLite | User account management |
| PyMuPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| python-pptx | PPTX text extraction |

## How to Run the Project

### Requirements
- Python 3.10 or later
- Google Gemini API key
- Internet connection

### Setup on Windows PowerShell

**1. Clone the repository**

```bash
git clone https://github.com/tejaswi580/DocuMind-AI.git
```

**2. Open the project folder**

```bash
cd DocuMind-AI
```

**3. Create a virtual environment**

```bash
py -m venv .venv
```

**4. Activate the virtual environment**

```powershell
.\.venv\Scripts\Activate.ps1
```

**5. Install the required packages**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**6. Configure the Gemini API key**

Set your API key as an environment variable in PowerShell:

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

Keep your API key private. Never upload it to GitHub.

**7. Run the application**

```bash
streamlit run app.py
```

## How RAG Works in This Project

1. **Document Loading:** Extract text from uploaded documents.
2. **Chunking:** Divide the extracted text into smaller chunks using 1000 characters as chunk size and 150 characters as overlap.
3. **Embedding:** Convert document chunks into numerical vectors using the Gemini embedding model (`gemini-embedding-001`).
4. **Storage:** Store chunks, embeddings and metadata in Streamlit session state.
5. **Retrieval:** Convert the user's question into an embedding and compare it with document embeddings using cosine similarity.
6. **Top-K Selection:** Retrieve the five most relevant chunks.
7. **Generation:** Send the retrieved context, question and selected answer format to the Gemini chat model.
8. **Output:** Display the generated answer in the Streamlit interface.

## Project Structure

```text
DocuMind-AI/
│
├── app.py
├── database.py
├── document_loader.py
├── chunking.py
├── rag_engine.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Team Members

| S.No | Member Name | Contribution |
|---|---|---|
| 1 | Member 1 Name | Add actual contribution |
| 2 | Member 2 Name | Add actual contribution |

## Limitations

- Scanned or image-based PDFs require OCR.
- Internet access is required for Gemini API operations.
- Embeddings and document chunks are stored temporarily in the active Streamlit session.
- The current version does not use a permanent vector database.
- Generated answers may sometimes contain inaccurate information.
- Login functionality is designed for a student project and is not production-grade authentication.

## Future Enhancements

- Persistent vector database integration
- OCR support for scanned documents
- Download generated answers as PDF
- Interactive MCQ quizzes and scoring
- Improved retrieval and answer accuracy
- Permanent document storage for individual users

## Conclusion

DocuMind AI combines RAG and LLM technology to help students prepare examination answers from their own study materials. It provides different answer formats based on marks and makes document-based learning easier and more interactive.

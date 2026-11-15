# 📚 DocuMind AI
### From Study Notes to Exam-Ready Answers

## About the Project

DocuMind AI is an AI-powered document-based study assistant developed using Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs).

It helps students prepare for examinations by uploading their study materials and generating answers based on the content of those documents.

Students can select different answer formats according to their examination requirements:

- 2 Marks
- 5 Marks
- 10 Marks
- Bits (MCQs)

The application retrieves relevant information from uploaded documents and uses an LLM to generate context-based answers.

##  Project Objective

The main objective of DocuMind AI is to make exam preparation easier by allowing students to interact with their own study materials.

Instead of manually searching through lengthy documents, students can upload their notes, ask questions, and receive answers in different examination formats.

##  Features

- User Registration and Login using SQLite
- Upload PDF, DOCX, PPTX, TXT and Markdown files
- Automatic text extraction from uploaded documents
- Text chunking with overlap
- Local embedding generation using Sentence Transformers
- Semantic similarity search using cosine similarity
- Retrieval of the top 5 relevant chunks
- Marks-based answer generation
- MCQ generation with five questions
- Source information display
- Download document embeddings as CSV
- Document fingerprinting to avoid unnecessary reprocessing of unchanged documents

##  Models Used

### 1. Embedding Model

**Model:** `sentence-transformers/all-MiniLM-L6-v2`

Purpose:
- Converts document chunks into numerical vectors.
- Converts user questions into numerical vectors.
- Helps identify semantically similar text.
- Generates 384-dimensional embeddings.
- Runs locally using the Sentence Transformers library.

### 2. Large Language Model (LLM)

**Model:** `openai/gpt-oss-120b`

**API Provider:** Groq

Purpose:
- Generates answers using the retrieved document context.
- Produces answers according to the selected marks format.
- Generates multiple-choice questions.
- Follows prompt instructions to answer using the supplied context.

##  Technologies and Libraries

| Technology / Library | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Frontend and application interface |
| Sentence Transformers | Local embedding generation |
| all-MiniLM-L6-v2 | Embedding model |
| Groq API | LLM-based answer generation |
| openai/gpt-oss-120b | Text generation model |
| NumPy | Vector operations and similarity calculation |
| SQLite | User account management |
| PyPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| python-pptx | PPTX text extraction |
| python-dotenv | Environment variable management |

##  How RAG Works in This Project

The project follows these steps:

1. **Document Loading:** The user uploads study materials. Text is extracted from the supported document formats.

2. **Chunking:** Extracted text is divided into smaller chunks using a chunk size of 1000 characters and an overlap of 150 characters.

3. **Embedding Generation:** The Sentence Transformer model converts each text chunk into a 384-dimensional numerical vector.

4. **Storage:** Text chunks, embeddings and metadata are stored temporarily in Streamlit session state.

5. **Question Embedding:** When the user asks a question, the same embedding model converts the question into a numerical vector.

6. **Similarity Search:** Cosine similarity is used to compare the question embedding with the stored document embeddings.

7. **Top-K Retrieval:** The five most relevant chunks are selected from the uploaded documents.

8. **Prompt Engineering:** The retrieved context, user question and selected answer format are provided to the LLM through a structured prompt.

9. **Answer Generation:** The Groq API uses the `openai/gpt-oss-120b` model to generate the answer.

10. **Output:** The generated answer is displayed in the Streamlit application.

##  Important Configuration Parameters

| Parameter | Value | Purpose |
|---|---|---|
| Chunk Size | 1000 characters | Defines the size of each text chunk |
| Chunk Overlap | 150 characters | Maintains context between consecutive chunks |
| Embedding Dimension | 384 | Size of each generated embedding vector |
| Batch Size | 32 | Number of texts processed together for embedding |
| Top-K | 5 | Number of relevant chunks retrieved |
| Similarity Method | Cosine Similarity | Measures similarity between vectors |
| Temperature | 0.1 | Controls response generation randomness |
| Maximum Completion Tokens | 4096 | Maximum token limit configured for generation |

##  Project Structure

```text
DocuMind-AI/
│
├── app.py
├── database.py
├── document_loader.py
├── chunking.py
├── rag_engine.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation and Execution

### Requirements

- Python 3.10 or later
- Groq API key
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

**6. Configure the Groq API key**

Create a `.env` file in the project folder and add:

```env
GROQ_API_KEY=your_groq_api_key
```

Keep your API key private. Never upload the `.env` file to GitHub.

**7. Run the application**

```bash
streamlit run app.py
```

The application will open in your web browser.

## 💾 Storage Details

DocuMind AI uses different storage methods for different purposes.

| Data | Storage |
|---|---|
| User account details | SQLite database |
| Document chunks | Streamlit session state |
| Embeddings | Streamlit session state |
| Document metadata | Streamlit session state |

The current version does not use a dedicated vector database such as FAISS, ChromaDB or Pinecone.

Document chunks and embeddings are stored temporarily in the active Streamlit session. They are not permanently saved in a vector database.

##  Limitations

- Scanned or image-based PDFs require OCR support.
- Internet access is required for Groq API operations.
- The first embedding-model use may require downloading the model.
- Document chunks and embeddings are stored temporarily in session memory.
- The current version does not use a permanent vector database.
- Generated answers may sometimes contain inaccurate information.
- Login functionality is designed for a student project and is not production-grade authentication.

##  Future Enhancements

- Integration with a persistent vector database.
- OCR support for scanned documents.
- Download generated answers as PDF.
- Interactive MCQ quizzes and automatic scoring.
- Improved retrieval and answer accuracy.
- Permanent document storage for individual users.
- Support for additional embedding and LLM models.

##  Conclusion

DocuMind AI combines Retrieval-Augmented Generation, Sentence Transformers and Large Language Models to make document-based learning easier.

It allows students to upload their study materials, ask questions and receive answers in different examination formats. By retrieving relevant information from uploaded documents before generating answers, the application provides a more focused and interactive study experience.

##  Project Information

**Project Name:** DocuMind AI

**Category:** Prompt Engineering and Retrieval-Augmented Generation

**Frontend:** Streamlit

**Embedding Model:** sentence-transformers/all-MiniLM-L6-v2

**LLM:** openai/gpt-oss-120b

**API Provider:** Groq

**GitHub Repository:** https://github.com/tejaswi580/DocuMind-AI

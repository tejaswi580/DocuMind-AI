
import re
import os
import html
from pathlib import Path

import numpy as np
import streamlit as st

from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from document_loader import extract_text
from chunking import split_into_chunks


# Load API key from project folder
load_dotenv(Path(__file__).resolve().parent / ".env")


# Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Local embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Groq chat model
CHAT_MODEL = "openai/gpt-oss-120b"


# Create Groq client
def get_client():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "Groq API key not found. "
            "Check GROQ_API_KEY in your .env file."
        )

    return Groq(api_key=api_key)


# Load local embedding model
@st.cache_resource
def get_embedding_model():

    model = SentenceTransformer(
        EMBEDDING_MODEL,
        device="cpu"
    )

    return model


# Generate local embeddings
def generate_embeddings(texts):

    if not texts:
        return np.empty((0, 384), dtype=np.float32)

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return np.asarray(vectors, dtype=np.float32)


# Process and index uploaded documents
def index_documents(uploaded_files):

    all_chunks = []
    metadata = []

    for uploaded_file in uploaded_files:

        text = extract_text(uploaded_file)

        if not text or not text.strip():
            continue

        chunks = split_into_chunks(
            text,
            CHUNK_SIZE,
            CHUNK_OVERLAP
        )

        for number, chunk in enumerate(chunks, start=1):

            all_chunks.append(chunk)

            metadata.append({
                "file": uploaded_file.name,
                "chunk": number
            })

    if not all_chunks:

        raise ValueError(
            "No readable text was found. "
            "Scanned PDFs need OCR before they can be searched."
        )

    # Generate embeddings locally
    with st.spinner("Generating local document embeddings..."):

        vectors = generate_embeddings(all_chunks)

    # Store document information in Streamlit session
    st.session_state.rag_chunks = all_chunks
    st.session_state.rag_metadata = metadata
    st.session_state.rag_vectors = vectors

    return {
        "files": len(uploaded_files),
        "chunks": len(all_chunks),
        "chunk_size": CHUNK_SIZE,
        "overlap": CHUNK_OVERLAP
    }


# Retrieve relevant document chunks
def retrieve(question, top_k=5):

    if "rag_vectors" not in st.session_state:

        raise ValueError(
            "No document index found. Process your documents first."
        )

    if not st.session_state.rag_chunks:

        raise ValueError(
            "No document chunks found. Process your documents again."
        )

    # Generate embedding for student question
    query_vectors = generate_embeddings([question])

    matrix = st.session_state.rag_vectors
    query = query_vectors[0]

    # Normalize document vectors
    matrix_norm = matrix / (
        np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    )

    # Normalize query vector
    query_norm = query / (
        np.linalg.norm(query) + 1e-10
    )

    # Calculate cosine similarity
    scores = matrix_norm @ query_norm

    # Select Top-K relevant chunks
    selected = np.argsort(scores)[::-1][
        :min(top_k, len(scores))
    ]

    passages = []

    for index in selected:

        passages.append({
            "text": st.session_state.rag_chunks[index],
            "file": st.session_state.rag_metadata[index]["file"],
            "chunk": st.session_state.rag_metadata[index]["chunk"],
            "score": float(scores[index])
        })

    return passages


# Format MCQ output
def format_mcq_output(text):

    text = html.unescape(text or "")
    text = text.replace("\r\n", "\n").strip()

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize option formatting
    text = re.sub(
        r"(?m)^\s*([A-Da-d])[).]\s*",
        lambda match: f"{match.group(1).upper()}) ",
        text
    )

    return text.strip()


# Generate answers based on selected answer type
def answer_question(question, answer_type):

    # Retrieve Top-5 relevant chunks
    passages = retrieve(question, top_k=5)

    # Prepare document context
    context = "\n\n".join(
        f"DOCUMENT: {p['file']} | CHUNK: {p['chunk']}\n{p['text']}"
        for p in passages
    )

    # Answer formats
    formats = {

        "2 Marks": """
Give a concise answer suitable for a 2-mark examination question.

TARGET LENGTH:
Approximately 40-60 words, depending on the available context.

Instructions:
- Start with a clear definition or direct answer.
- Include 2-4 important points.
- Use simple and clear language.
- Avoid unnecessary explanations.
""",

        "5 Marks": """
Give a well-organized answer suitable for a 5-mark examination question.

TARGET LENGTH:
Approximately 150-200 words, depending on the available context.

Follow this structure:
1. Introduction or definition.
2. Explain the important points.
3. Include relevant features, types or steps.
4. Add an example if available in the document.
5. End with a short conclusion.

Instructions:
- Explain every important point in 2-3 meaningful sentences.
- Use suitable headings and subheadings.
- Do not provide only keywords or lists.
""",

        "10 Marks": """
Generate a comprehensive and detailed answer suitable for a
10-mark university examination question.

TARGET LENGTH:
Approximately 400-500 words, depending on the amount of
relevant information available in the retrieved context.

FOLLOW THIS STRUCTURE:

1. Introduction and Definition:
   Introduce the topic and explain its meaning clearly.
   Write a meaningful paragraph.

2. Objectives / Importance:
   Explain each relevant objective or important point.
   Do not simply list keywords.

3. Main Explanation:
   Divide the topic into suitable headings and subheadings.
   Explain every heading in complete sentences.

4. Detailed Points:
   For every important numbered point:
   - Explain what the point means.
   - Explain why it is important.
   - Describe its purpose or application.
   - Include an example if the context provides one.

   Each important point should contain approximately
   3-5 meaningful sentences wherever the context supports it.

5. Features / Types / Principles / Steps:
   Include only the sections relevant to the question.
   Explain every listed feature, type, principle or step.
   Never provide only a list of headings or keywords.

6. Examples:
   Include suitable examples only if they are available
   in the retrieved document context.

7. Advantages / Benefits:
   Explain the relevant advantages with meaningful details
   wherever the context contains this information.

8. Conclusion:
   End with a short paragraph summarising the main idea.

IMPORTANT RULES:
- Every main heading and subheading must have explanatory content.
- Do not leave any heading without an explanation.
- Do not write only bullet points or keywords.
- Use complete sentences and clear academic language.
- Maintain a logical flow between sections.
- Avoid repeating the same information.
- Do not force irrelevant headings into the answer.
- Do not invent examples, advantages or facts.
- Use only information supported by the retrieved context.
- If the retrieved context does not contain enough information,
  clearly mention the limitation instead of inventing content.
""",

        "Bits (MCQs)": """
Generate exactly 5 multiple-choice questions (MCQs) based
strictly on the supplied document context.

For each question:
- Provide 4 options: A, B, C and D.
- Only one option must be correct.
- Make the questions clear and relevant.
- Avoid duplicate questions.

After all 5 questions:
- Provide an Answer Key.
- Give a short explanation for each correct answer.
- Ensure every correct answer is supported by the context.
"""
    }

    # System instructions
    system_prompt = """
You are DocuMind AI, a careful document-based study assistant.

Your main responsibility is to help students prepare examination
answers using their uploaded study materials.

STRICT RULES:

1. Use ONLY the supplied retrieved document context.
2. Do not use outside knowledge or assumptions.
3. Never invent facts, definitions, examples or explanations.
4. If the context does not contain enough information, clearly say:

"The uploaded documents do not provide enough information
to answer this question."

5. You may combine relevant information from multiple retrieved
passages without changing their original meaning.

6. Follow the answer format selected by the student.

7. For 5-mark and 10-mark answers, explain every important
heading and subheading in complete sentences.

8. Never provide only headings, keywords or unexplained
bullet points when a detailed answer is requested.

9. Use simple academic English suitable for university examinations.

10. For MCQs, every question, option, correct answer and
explanation must be supported by the supplied context.

11. Do not pretend that information came from a document
if it is not present in the retrieved context.
"""

    # User prompt
    user_prompt = f"""
Selected Answer Format:
{answer_type}

Answer Instructions:
{formats[answer_type]}

Student Question:
{question}

Retrieved Document Context:
{context}

Generate the answer now.

Important:
Follow the selected answer format carefully.
For 10-mark answers, explain every heading and point in detail.
Do not provide headings without explanations.
Use only the retrieved document context.
"""

    # Create Groq client
    client = get_client()

    # Generate response using Groq
    result = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.1,
        max_completion_tokens=4096
    )

    answer = result.choices[0].message.content or ""

    # Format MCQ response
    if answer_type == "Bits (MCQs)":

        answer = format_mcq_output(answer)

    return answer, passages


# Clear document index from Streamlit session
def clear_session_index():

    for key in [
        "rag_chunks",
        "rag_metadata",
        "rag_vectors",
        "doc_ready"
    ]:

        st.session_state.pop(key, None)

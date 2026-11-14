
import re
import os
from pathlib import Path

import numpy as np
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from document_loader import extract_text
from chunking import split_into_chunks


# Load API key from the project folder
load_dotenv(Path(__file__).resolve().parent / ".env")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-3.5-flash-lite"


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key not found. "
            "Check GEMINI_API_KEY in your .env file."
        )

    return genai.Client(api_key=api_key)


def generate_embeddings(client, texts, task_type):
    vectors = []
    batch_size = 32

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]

        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=768
            )
        )

        vectors.extend(
            embedding.values for embedding in result.embeddings
        )

    return np.array(vectors, dtype=np.float32)


def index_documents(uploaded_files):
    client = get_client()

    all_chunks = []
    metadata = []

    for uploaded_file in uploaded_files:
        text = extract_text(uploaded_file)

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

    vectors = generate_embeddings(
        client,
        all_chunks,
        "RETRIEVAL_DOCUMENT"
    )

    st.session_state.rag_chunks = all_chunks
    st.session_state.rag_metadata = metadata
    st.session_state.rag_vectors = vectors

    return {
        "files": len(uploaded_files),
        "chunks": len(all_chunks),
        "chunk_size": CHUNK_SIZE,
        "overlap": CHUNK_OVERLAP
    }


def retrieve(question, top_k=5):
    if "rag_vectors" not in st.session_state:
        raise ValueError(
            "No document index found. Process your documents first."
        )

    client = get_client()

    query_vectors = generate_embeddings(
        client,
        [question],
        "RETRIEVAL_QUERY"
    )

    matrix = st.session_state.rag_vectors
    query = query_vectors[0]

    matrix_norm = matrix / (
        np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    )

    query_norm = query / (
        np.linalg.norm(query) + 1e-10
    )

    scores = matrix_norm @ query_norm

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


# Fix MCQ formatting even if Gemini puts options on one line

def format_mcq_output(text):

    # Put every MCQ heading on a separate section
    text = re.sub(
        r'\s*(MCQ\s*\d+)',
        r'\n\n\1\n\n',
        text,
        flags=re.IGNORECASE
    )

    # Put the question on its own line
    text = re.sub(
        r'\s*(Question:)',
        r'\n\n\1',
        text,
        flags=re.IGNORECASE
    )

    # Put each option A, B, C, D on a separate line
    text = re.sub(
        r'\s+([A-D])\)\s*',
        r'\n\n\1) ',
        text
    )

    # Keep answer key and explanations in separate sections
    text = re.sub(
        r'\s*(ANSWER KEY)',
        r'\n\nANSWER KEY\n\n',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'\s*(EXPLANATIONS)',
        r'\n\nEXPLANATIONS\n\n',
        text,
        flags=re.IGNORECASE
    )

    # Clean excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()



def answer_question(question, answer_type):
    client = get_client()

    passages = retrieve(question, top_k=5)

    context = "\n\n".join(
        f"DOCUMENT: {p['file']} | CHUNK: {p['chunk']}\n{p['text']}"
        for p in passages
    )

    formats = {
        "2 Marks": (
            "Give a concise answer suitable for a 2-mark exam "
            "question, usually 2-4 key points or a short paragraph."
        ),

        "5 Marks": (
            "Give a well-organized answer suitable for a 5-mark "
            "exam question, with a short introduction and "
            "4-6 important points."
        ),

        "10 Marks": (
            "Give a detailed, structured answer suitable for a "
            "10-mark exam question, with headings, explanation, "
            "and examples only if supported by the context."
        ),

        "Bits (MCQs)": """
Generate exactly 5 multiple-choice questions using ONLY
the uploaded document context.

STRICT OUTPUT FORMAT:

MCQ 1

Question: Write the first question here?

A) First option
B) Second option
C) Third option
D) Fourth option

MCQ 2

Question: Write the second question here?

A) First option
B) Second option
C) Third option
D) Fourth option

Continue in the same format until MCQ 5.

IMPORTANT RULES:

1. Generate exactly 5 questions.
2. Every question must have exactly 4 options.
3. Put A, B, C and D on separate lines.
4. Never put two options on the same line.
5. Do not reveal the correct answer below a question.
6. Show all five questions before the answer key.
7. Do not repeat questions.

AFTER ALL FIVE QUESTIONS, SHOW:

ANSWER KEY

1. Correct option letter
2. Correct option letter
3. Correct option letter
4. Correct option letter
5. Correct option letter

EXPLANATIONS

1. Explanation for question 1.
2. Explanation for question 2.
3. Explanation for question 3.
4. Explanation for question 4.
5. Explanation for question 5.

Make sure the answers and explanations match the
questions and options exactly.

Every question, option, answer and explanation must
come from the supplied document context.

Do not use outside knowledge or invent information.
"""
    }

    system_prompt = """
You are StudyMate, a careful study assistant.

Use ONLY the supplied document context to answer.

Do not use outside knowledge, assumptions, or invented facts.

If the context does not contain enough information, clearly say:

'The uploaded documents do not provide enough information to answer this question.'

You may combine relevant statements from multiple retrieved
passages, but do not change their meaning.

For MCQs, every question, option, correct answer and explanation
must be supported by the context.

Do not pretend that a statement came from a document if it is
not present there.
"""

    user_prompt = f"""
Answer format: {formats[answer_type]}

Student question:
{question}

Retrieved document context:
{context}

Write the answer now. Stay strictly within the context.
"""

    result = client.models.generate_content(
        model=CHAT_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1
        )
    )

    answer = result.text or ""

    # Apply special formatting only to MCQ answers
    if answer_type == "Bits (MCQs)":
        answer = format_mcq_output(answer)

    return answer, []


def clear_session_index():
    for key in [
        "rag_chunks",
        "rag_metadata",
        "rag_vectors",
        "doc_ready"
    ]:
        st.session_state.pop(key, None)

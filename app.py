
import streamlit as st
import io
import numpy as np

from database import init_db, create_user, verify_user
from rag_engine import index_documents, answer_question, clear_session_index

# Page configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide"
)

init_db()

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# Login and Registration Screen
def login_screen():

    st.markdown(
        "<h1 style='text-align:center'>📚 DocuMind AI</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center'>From Study Notes to Exam-Ready Answers.</p>",
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1, 1.2, 1])

    with center:

        mode = st.radio(
            "Choose",
            ["Login", "Create account"],
            horizontal=True
        )

        with st.form("auth_form"):

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button(
                mode,
                use_container_width=True
            )

        if submitted:

            if not username.strip() or not password:
                st.error("Enter both username and password.")

            elif mode == "Create account":

                ok, msg = create_user(username.strip(), password)
                (st.success if ok else st.error)(msg)

            else:

                if verify_user(username.strip(), password):

                    st.session_state.user = username.strip()
                    st.rerun()

                else:
                    st.error("Incorrect username or password.")


# Check Login
if not st.session_state.user:

    login_screen()
    st.stop()


# Sidebar
with st.sidebar:

    st.title("DocuMind AI")

    st.write(f"Signed in as **{st.session_state.user}**")

    # Logout
    if st.button("Log out", use_container_width=True):

        st.session_state.user = None
        st.session_state.messages = []

        clear_session_index()

        st.rerun()

    st.divider()

    # Upload Documents
    st.subheader("1. Upload your documents")

    uploads = st.file_uploader(
        "Upload PDF, DOCX, PPTX, TXT or MD files",
        type=["pdf", "docx", "pptx", "txt", "md"],
        accept_multiple_files=True
    )

    # Process Documents
    if st.button(
        "Process documents",
        type="primary",
        use_container_width=True
    ):

        if not uploads:

            st.warning("Please upload at least one document.")

        else:

            with st.spinner(
                "Reading, chunking and creating embeddings..."
            ):

                try:

                    stats = index_documents(uploads)

                    st.session_state.doc_ready = True

                    st.success(
                        f"Processed {stats['files']} file(s) "
                        f"into {stats['chunks']} chunks."
                    )

                    st.caption(
                        f"Chunk size: {stats['chunk_size']} characters "
                        f"| Overlap: {stats['overlap']} characters"
                    )

                except Exception as exc:

                    st.error(str(exc))

    st.divider()

    # Download Embeddings
    st.subheader("2. Download Embeddings")

    if "rag_vectors" in st.session_state:

        csv_buffer = io.StringIO()

        np.savetxt(
            csv_buffer,
            st.session_state.rag_vectors,
            delimiter=",",
            fmt="%.8f"
        )

        st.download_button(
            label="Download Embeddings (CSV)",
            data=csv_buffer.getvalue(),
            file_name="studymate_embeddings.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:

        st.info(
            "Process your documents first to download embeddings."
        )

    st.divider()

    # Answer Format
    st.subheader("3. Choose answer format")

    answer_type = st.selectbox(
        "Answer length",
        ["2 Marks", "5 Marks", "10 Marks", "Bits (MCQs)"]
    )

    # Clear Chat
    if st.button("Clear chat", use_container_width=True):

        st.session_state.messages = []

        st.rerun()


# Main Dashboard
st.title("From Study Notes to Exam-Ready Answers.")

st.write(
    "Upload your class notes or study material, "
    "then ask questions. Answers are generated "
    "using the uploaded content."
)

st.info(
    "For document-grounded answers, process your files first. "
    "The assistant will say when the uploaded material "
    "does not contain enough information."
)


# Display Previous Chat Messages
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])


# Chat Input
question = st.chat_input(
    "Ask a question from your uploaded documents..."
)

if question:

    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        if not st.session_state.get("doc_ready"):

            response = (
                "Please upload and process your documents "
                "in the sidebar first."
            )

        else:

            with st.spinner(
                "Finding relevant passages and preparing your answer..."
            ):

                try:

                    response, sources = answer_question(
                        question,
                        answer_type
                    )

                    if sources:

                        response += (
                            "\n\n**Sources from your uploaded documents:**\n"
                            + "\n".join(
                                f"- {s['file']} (chunk {s['chunk']})"
                                for s in sources
                            )
                        )

                except Exception as exc:

                    response = f"Could not generate an answer: {exc}"

        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

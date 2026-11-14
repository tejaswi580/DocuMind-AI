from io import BytesIO
from pathlib import Path
import fitz
from docx import Document
from pptx import Presentation

SUPPORTED = {".pdf", ".docx", ".pptx", ".txt", ".md"}

def extract_text(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    data = uploaded_file.getvalue()

    if suffix not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".pdf":
        pdf = fitz.open(stream=data, filetype="pdf")
        pages = []
        for page_no, page in enumerate(pdf, start=1):
            text = page.get_text("text")
            if text.strip():
                pages.append(f"[Page {page_no}]\n{text}")
        return "\n\n".join(pages)

    if suffix == ".docx":
        doc = Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if suffix == ".pptx":
        presentation = Presentation(BytesIO(data))
        slides = []
        for slide_no, slide in enumerate(presentation.slides, start=1):
            lines = [shape.text for shape in slide.shapes if hasattr(shape, "text_frame") and shape.text.strip()]
            if lines:
                slides.append(f"[Slide {slide_no}]\n" + "\n".join(lines))
        return "\n\n".join(slides)

    return data.decode("utf-8", errors="ignore")

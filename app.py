import os
from io import BytesIO
import streamlit as st
from groq import Groq
from workflow import create_context, run_workflow

DEFAULT_MODEL = "openai/gpt-oss-120b"

st.set_page_config(page_title="AI Study Pack Generator", page_icon="📚", layout="wide")

def get_api_key():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        try:
            key = st.secrets["GROQ_API_KEY"].strip()
        except Exception:
            key = ""
    return key

def extract_uploaded_text(uploaded_file):
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    data = uploaded_file.read()
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        from docx import Document
        doc = Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file type.")

st.title("📚 AI Study Pack Generator")
st.caption("Multi-stage AI workflow: Planning → Content Generation → Assessment → Review → Refinement")

with st.sidebar:
    st.header("Study Settings")
    level = st.selectbox("Student Level", ["Beginner", "Intermediate", "BS University", "Advanced"], index=2)
    pack_type = st.selectbox("Study Pack Type", [
        "Complete Study Pack", "Exam Revision Pack",
        "Concept Understanding Pack", "Quick Revision Pack"
    ])
    flashcards = st.slider("Number of Flashcards", 5, 30, 10)
    mcqs = st.slider("Number of MCQs", 5, 30, 10)
    model = st.text_input("Groq Model", DEFAULT_MODEL)

topic = st.text_input("📌 Topic", placeholder="Example: Heat Transfer")
uploaded = st.file_uploader("📄 Upload study material (optional)", type=["txt", "pdf", "docx"])
pasted = st.text_area("📝 Paste study material (optional)", height=220)

material = pasted.strip()
if uploaded:
    try:
        uploaded_text = extract_uploaded_text(uploaded)
        material = f"{material}\n\n{uploaded_text}".strip()
        st.success(f"Loaded {len(uploaded_text.split())} words from {uploaded.name}.")
    except Exception as e:
        st.error(f"Could not read file: {e}")

if st.button("🚀 Generate Study Pack", type="primary", use_container_width=True):
    if not topic.strip() and not material.strip():
        st.warning("Enter a topic or provide study material.")
        st.stop()

    api_key = get_api_key()
    if not api_key:
        st.error("GROQ_API_KEY is missing. Add it to Streamlit Secrets.")
        st.stop()

    client = Groq(api_key=api_key)
    context = create_context(topic, material, level, pack_type, flashcards, mcqs, model)

    st.subheader("🔄 AI Workflow")
    progress = st.progress(0)
    status = st.empty()

    def update_progress(number, name):
        progress.progress(int((number - 1) / 5 * 100))
        status.info(f"Stage {number}/5: **{name}**")

    result = run_workflow(context, client, update_progress)

    if result["workflow"]["errors"]:
        status.error("Workflow stopped because a stage failed.")
        for error in result["workflow"]["errors"]:
            st.error(error)
        st.stop()

    progress.progress(100)
    status.success("✅ All five stages completed successfully.")

    with st.expander("🔍 Workflow Review"):
        st.write("Completed stages:", result["workflow"]["completed_stages"])
        score = result["review"].get("quality_score", "N/A")
        st.metric("Review Quality Score", f"{score}/100" if isinstance(score, (int, float)) else score)
        st.json(result["review"])

    final_pack = result["refinement"].get("final_study_pack", "")
    st.subheader("📖 Final Study Pack")
    st.markdown(final_pack)

    st.download_button(
        "⬇️ Download Study Pack",
        data=final_pack,
        file_name="AI_Study_Pack.md",
        mime="text/markdown",
        use_container_width=True,
    )

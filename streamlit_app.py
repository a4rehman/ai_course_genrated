import streamlit as st
import os
import json
import pathlib
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AI Healthcare Training (Gemini Edition)",
    page_icon="🏥",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .stApp { background: #0f172a; color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 10px; background: #3b82f6; color: white; }
</style>
""", unsafe_allow_html=True)

# Path Configuration
PROJECT_ROOT = pathlib.Path(__file__).parent
MODULES_DIR = PROJECT_ROOT / "modules"
PROMPTS_FILE = PROJECT_ROOT / "prompts" / "claude_prompts.json" # Kept filename for compatibility

# Sidebar
with st.sidebar:
    st.title("🏥 Gemini Training Gen")
    # Try Streamlit Cloud secrets first, then env var, then sidebar input
    _secret_key = ""
    try:
        _secret_key = st.secrets.get("Gemini_API_Key", "")
    except Exception:
        pass
    gemini_key = st.text_input(
        "Google Gemini API Key",
        value=_secret_key or os.getenv("Gemini_API_Key", ""),
        type="password"
    )
    if gemini_key:
        genai.configure(api_key=gemini_key)
    else:
        st.warning("Please provide a Gemini API Key")

    st.divider()
    course_list = [
        "Family Caregiver Training",
        "Handwashing and Glove Use in Personal Care",
        "Introduction to Cultural and Diversity Training",
        "Personal Care Worker (PCW) Foundations Training",
        "Trauma-Informed & Culturally Competent Care Training",
        "Community Health Worker Training"
    ]
    selected_courses = st.multiselect("Select Modules", course_list, default=course_list)

# Load Prompts
if PROMPTS_FILE.exists():
    PROMPTS = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))

def call_gemini(system, user):
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=system)
    response = model.generate_content(user)
    return response.text

def generate_module(topic, m_id):
    m_path = MODULES_DIR / f"module_{m_id}"
    m_path.mkdir(parents=True, exist_ok=True)
    
    with st.status(f"Generating {topic}..."):
        # Lesson
        st.write("Creating lesson...")
        lesson = call_gemini(PROMPTS["lesson"]["system"], PROMPTS["lesson"]["user"].format(topic=topic))
        (m_path / "lesson.md").write_text(lesson, encoding="utf-8")
        
        # Quiz
        st.write("Creating quiz...")
        quiz = call_gemini(PROMPTS["quiz"]["system"], PROMPTS["quiz"]["user"].format(topic=topic))
        quiz = quiz.replace("```json", "").replace("```", "").strip()
        (m_path / "quiz.json").write_text(quiz, encoding="utf-8")
        
        # Visuals
        st.write("Creating visuals...")
        visuals = call_gemini(PROMPTS["visual"]["system"], PROMPTS["visual"]["user"].format(topic=topic))
        (m_path / "visual.md").write_text(visuals, encoding="utf-8")

st.title("🏥 Healthcare Training Content Generator")
st.info("Using Google Gemini 2.0 Flash to generate professional medical training content.")

tab1, tab2 = st.tabs(["🚀 Generate", "📚 Library"])

with tab1:
    if st.button("Generate Selected Modules"):
        if not gemini_key:
            st.error("API Key missing!")
        else:
            for i, topic in enumerate(selected_courses, 1):
                generate_module(topic, i)
            st.success("All modules generated!")
            st.balloons()

with tab2:
    modules = sorted(list(MODULES_DIR.glob("module_*")))
    if not modules:
        st.write("No modules found.")
    else:
        for m in modules:
            m_id = m.name.split("_")[1]
            lesson_file = m / "lesson.md"
            if lesson_file.exists():
                title = lesson_file.read_text().split("\n")[0].replace("#", "").strip()
                with st.expander(f"Module {m_id}: {title}"):
                    st.markdown(lesson_file.read_text())
                    if (m / "quiz.json").exists():
                        st.divider()
                        st.subheader("Quiz Content")
                        st.code((m / "quiz.json").read_text())

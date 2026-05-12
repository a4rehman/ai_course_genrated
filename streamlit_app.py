import streamlit as st
import os
import json
import pathlib
import requests
import markdown
from typing import List, Dict

# Set page config
st.set_page_config(
    page_title="AI Healthcare Training Generator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
        color: #e6edf3;
    }
    .module-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .module-card:hover {
        transform: translateY(-5px);
        border-color: #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
PROJECT_ROOT = pathlib.Path(__file__).parent
MODULES_DIR = PROJECT_ROOT / "modules"
PROMPTS_FILE = PROJECT_ROOT / "prompts" / "claude_prompts.json"
HISTORY_FILE = PROJECT_ROOT / "prompts" / "prompt_history.json"

# Ensure directories exist
MODULES_DIR.mkdir(exist_ok=True)
(PROJECT_ROOT / "prompts").mkdir(exist_ok=True)

# Sidebar - API Configuration
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Anthropic API Key", type="password", help="Enter your Claude API key")
    if not api_key:
        st.warning("Please enter an API key to enable generation.")
    
    st.divider()
    st.subheader("Courses to Generate")
    course_list = [
        "Family Caregiver Training",
        "Handwashing and Glove Use in Personal Care",
        "Introduction to Cultural and Diversity Training",
        "Personal Care Worker (PCW) Foundations Training",
        "Trauma-Informed & Culturally Competent Care Training",
        "Community Health Worker Training"
    ]
    selected_courses = st.multiselect("Select modules", course_list, default=course_list)

# Main Title
st.title("🏥 AI Healthcare Training Suite")
st.markdown("### Generate Professional, Human-Like Training Modules in Minutes")

# Load prompts
if PROMPTS_FILE.exists():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        PROMPTS = json.load(f)
else:
    st.error("Prompts file not found!")
    st.stop()

def call_claude(system_prompt: str, user_prompt: str, key: str) -> str:
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 4096,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
    if response.status_code != 200:
        st.error(f"Error from Claude: {response.text}")
        return ""
    return response.json()["content"][0]["text"]

def generate_module(topic: str, module_id: int, key: str):
    module_path = MODULES_DIR / f"module_{module_id}"
    module_path.mkdir(exist_ok=True)
    
    progress_bar = st.progress(0, text=f"Generating {topic}...")
    
    # 1. Lesson
    progress_bar.progress(20, text="Generating lesson content...")
    lesson_md = call_claude(PROMPTS["lesson"]["system"], PROMPTS["lesson"]["user"].format(topic=topic), key)
    (module_path / "lesson.md").write_text(lesson_md, encoding="utf-8")
    
    # 2. Quiz
    progress_bar.progress(50, text="Generating quiz questions...")
    quiz_json_str = call_claude(PROMPTS["quiz"]["system"], PROMPTS["quiz"]["user"].format(topic=topic), key)
    (module_path / "quiz.json").write_text(quiz_json_str, encoding="utf-8")
    
    # 3. Visuals
    progress_bar.progress(80, text="Generating visual guidance...")
    visual_md = call_claude(PROMPTS["visual"]["system"], PROMPTS["visual"]["user"].format(topic=topic), key)
    (module_path / "visual.md").write_text(visual_md, encoding="utf-8")
    
    progress_bar.progress(100, text="Done!")
    return True

# Tabs
tab1, tab2, tab3 = st.tabs(["🚀 Generator", "📚 Course Library", "📜 Prompt History"])

with tab1:
    st.header("Module Generation Hub")
    if st.button("Generate Selected Modules", disabled=not api_key):
        for i, topic in enumerate(selected_courses, 1):
            with st.status(f"Processing Module {i}: {topic}"):
                success = generate_module(topic, i, api_key)
                if success:
                    st.success(f"Module {i} complete!")
        st.balloons()

with tab2:
    st.header("Your Training Library")
    
    # Check for existing modules
    existing_modules = sorted(list(MODULES_DIR.glob("module_*")))
    
    if not existing_modules:
        st.info("No modules generated yet. Use the Generator tab to get started.")
    else:
        for m_path in existing_modules:
            m_id = m_path.name.split("_")[1]
            lesson_file = m_path / "lesson.md"
            if lesson_file.exists():
                content = lesson_file.read_text(encoding="utf-8")
                title = content.split("\n")[0].replace("#", "").strip()
                
                with st.expander(f"Module {m_id}: {title}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(content)
                    with col2:
                        st.subheader("Quiz Preview")
                        quiz_file = m_path / "quiz.json"
                        if quiz_file.exists():
                            try:
                                quiz_data = json.loads(quiz_file.read_text(encoding="utf-8"))
                                for i, q in enumerate(quiz_data, 1):
                                    st.write(f"**Q{i}:** {q['question']}")
                            except:
                                st.code(quiz_file.read_text(encoding="utf-8"))
                        
                        st.divider()
                        st.subheader("Visual Guidance")
                        visual_file = m_path / "visual.md"
                        if visual_file.exists():
                            st.markdown(visual_file.read_text(encoding="utf-8"))

with tab3:
    st.header("Claude Prompt Engineering")
    st.json(PROMPTS)
    if HISTORY_FILE.exists():
        st.subheader("Generation History")
        st.json(json.loads(HISTORY_FILE.read_text(encoding="utf-8")))

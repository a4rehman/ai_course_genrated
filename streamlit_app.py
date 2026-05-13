"""
AI Healthcare Training Content Generator — Streamlit App.
Uses Google Gemini 2.0 Flash to generate lessons, quizzes, and visual guides.
"""

import streamlit as st
import os
import json
import pathlib
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Healthcare Training Generator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, .stApp { font-family: 'Inter', sans-serif; background: #0b0f1a !important; color: #f1f5f9; }
#MainMenu, footer, header { visibility: hidden; }

section[data-testid="stSidebar"] { background: #111827 !important; border-right: 1px solid rgba(99,102,241,0.2); }

.hero-title {
    font-size: 2.4rem; font-weight: 800; text-align: center;
    background: linear-gradient(135deg, #60A5FA, #6366F1, #A78BFA);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-sub { text-align: center; color: #64748B; font-size: 1rem; margin-bottom: 1.5rem; }
.gradient-divider { height: 2px; background: linear-gradient(90deg, transparent, #6366F1, transparent); margin: 1.5rem 0; border: none; }

.module-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.04));
    border: 1px solid rgba(99,102,241,0.2); border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
}
.module-card h4 { color: #818CF8; margin: 0 0 0.5rem 0; font-size: 1.05rem; }

.quiz-question {
    background: rgba(17,24,39,0.8); border: 1px solid rgba(99,102,241,0.15);
    border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
}
.quiz-question p { margin: 0 0 0.5rem 0; font-weight: 600; color: #E2E8F0; }

.correct   { color: #22C55E; font-weight: 600; }
.incorrect { color: #EF4444; font-weight: 600; }

.stat-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.06));
    border: 1px solid rgba(99,102,241,0.25); border-radius: 12px; padding: 1rem; text-align: center;
}
.stat-value { font-size: 1.8rem; font-weight: 700; color: #818CF8; }
.stat-label { font-size: 0.8rem; color: #9CA3AF; margin-top: 0.2rem; }

div[data-testid="stTabs"] button { color: #9CA3AF; font-weight: 500; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #818CF8 !important; border-bottom-color: #6366F1 !important; }
</style>
""", unsafe_allow_html=True)

# ── Paths ──────────────────────────────────────────────────────────
ROOT        = pathlib.Path(__file__).parent
MODULES_DIR = ROOT / "modules"
PROMPTS_FILE = ROOT / "prompts" / "claude_prompts.json"
MODULES_DIR.mkdir(exist_ok=True)

# ── Load Prompts ───────────────────────────────────────────────────
if not PROMPTS_FILE.exists():
    st.error(f"Prompts file not found: {PROMPTS_FILE}")
    st.stop()
PROMPTS = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 Healthcare Training Gen")
    st.caption("Powered by Google Gemini AI")
    st.divider()

    # API Key — try secrets, then env, then manual input
    _secret_key = ""
    try:
        _secret_key = st.secrets.get("Gemini_API_Key", "")
    except Exception:
        pass
    gemini_key = st.text_input(
        "🔑 Google Gemini API Key",
        value=_secret_key or os.getenv("Gemini_API_Key", ""),
        type="password",
        help="Get your key from https://aistudio.google.com/app/apikey"
    )
    if gemini_key:
        genai.configure(api_key=gemini_key)
        st.success("API Key configured ✓", icon="✅")
    else:
        st.warning("Enter your Gemini API Key to start.")

    st.divider()

    COURSE_LIST = [
        "Family Caregiver Training",
        "Handwashing and Glove Use in Personal Care",
        "Introduction to Cultural and Diversity Training",
        "Personal Care Worker (PCW) Foundations Training",
        "Trauma-Informed & Culturally Competent Care Training",
        "Community Health Worker Training",
    ]
    selected_courses = st.multiselect(
        "📚 Select Modules to Generate",
        COURSE_LIST,
        default=COURSE_LIST[:2],
    )
    
    st.divider()
    selected_model = st.selectbox(
        "🤖 Select AI Model",
        ["gemini-3-flash", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
        help="Use the model that has active quota in your Google AI Studio dashboard."
    )
    st.caption(f"Using {selected_model}")

# ── Gemini Call ────────────────────────────────────────────────────
def call_gemini(system: str, user: str, model_name: str) -> str:
    try:
        model = genai.GenerativeModel(model_name, system_instruction=system)
        response = model.generate_content(user)
        return response.text
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")

# ── Module Generation ──────────────────────────────────────────────
def generate_module(topic: str, m_id: int):
    m_path = MODULES_DIR / f"module_{m_id}"
    m_path.mkdir(parents=True, exist_ok=True)

    with st.status(f"⚙️ Generating: {topic}", expanded=True) as status:
        st.write("📖 Writing lesson content...")
        lesson = call_gemini(PROMPTS["lesson"]["system"], PROMPTS["lesson"]["user"].format(topic=topic), selected_model)
        (m_path / "lesson.md").write_text(lesson, encoding="utf-8")

        st.write("❓ Creating quiz questions...")
        quiz_raw = call_gemini(PROMPTS["quiz"]["system"], PROMPTS["quiz"]["user"].format(topic=topic), selected_model)
        quiz_raw = quiz_raw.replace("```json", "").replace("```", "").strip()
        try:
            quiz_data = json.loads(quiz_raw)
        except json.JSONDecodeError:
            quiz_data = []
        (m_path / "quiz.json").write_text(json.dumps(quiz_data, indent=2, ensure_ascii=False), encoding="utf-8")

        st.write("🎨 Generating slide visual guidance...")
        visuals = call_gemini(PROMPTS["visual"]["system"], PROMPTS["visual"]["user"].format(topic=topic), selected_model)
        (m_path / "visual.md").write_text(visuals, encoding="utf-8")

        status.update(label=f"✅ {topic} — Done!", state="complete")


# ══════════════════════════════════════════════════════════════════
#  MAIN UI
# ══════════════════════════════════════════════════════════════════
st.markdown('<h1 class="hero-title">🏥 AI Healthcare Training Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Generate professional healthcare training content instantly using Gemini AI</p>', unsafe_allow_html=True)
st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

tab_gen, tab_lib, tab_quiz = st.tabs(["🚀 Generate", "📚 Module Library", "❓ Take Quiz"])

# ── Tab 1: Generate ────────────────────────────────────────────────
with tab_gen:
    if not selected_courses:
        st.info("Select at least one module from the sidebar to get started.")
    else:
        st.markdown(f"**{len(selected_courses)} module(s) selected for generation:**")
        cols = st.columns(3)
        for i, c in enumerate(selected_courses):
            cols[i % 3].markdown(f"- {c}")

        st.markdown("")
        if st.button("🚀 Generate Selected Modules", type="primary", use_container_width=True):
            if not gemini_key:
                st.error("❌ Please enter your Gemini API Key in the sidebar first.")
            else:
                try:
                    for i, topic in enumerate(selected_courses, 1):
                        generate_module(topic, i)
                    st.success("🎉 All modules generated successfully!")
                    st.balloons()
                    st.rerun()
                except RuntimeError as e:
                    st.error(f"❌ {e}")
                    st.info("💡 If the error says 'NotFound' or 'Quota Exceeded', try switching the model in the sidebar.")

# ── Tab 2: Module Library ──────────────────────────────────────────
with tab_lib:
    modules = sorted(MODULES_DIR.glob("module_*"))
    if not modules:
        st.info("No modules generated yet. Go to the **Generate** tab to create your first module.")
    else:
        # Stats
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{len(modules)}</div><div class="stat-label">Modules Generated</div></div>', unsafe_allow_html=True)
        with s2:
            quiz_count = sum(1 for m in modules if (m / "quiz.json").exists())
            st.markdown(f'<div class="stat-card"><div class="stat-value">{quiz_count}</div><div class="stat-label">Quizzes Available</div></div>', unsafe_allow_html=True)
        with s3:
            visual_count = sum(1 for m in modules if (m / "visual.md").exists())
            st.markdown(f'<div class="stat-card"><div class="stat-value">{visual_count}</div><div class="stat-label">Visual Guides</div></div>', unsafe_allow_html=True)

        st.markdown("")

        for m in modules:
            lesson_file = m / "lesson.md"
            quiz_file   = m / "quiz.json"
            visual_file = m / "visual.md"

            if not lesson_file.exists():
                continue

            lesson_text = lesson_file.read_text(encoding="utf-8")
            title = lesson_text.split("\n")[0].replace("#", "").strip() or m.name

            with st.expander(f"📘 {title}"):
                inner_tab1, inner_tab2, inner_tab3 = st.tabs(["📖 Lesson", "🎨 Visual Guide", "📥 Download"])

                with inner_tab1:
                    st.markdown(lesson_text)

                with inner_tab2:
                    if visual_file.exists():
                        st.markdown(visual_file.read_text(encoding="utf-8"))
                    else:
                        st.info("No visual guide available.")

                with inner_tab3:
                    dl1, dl2, dl3 = st.columns(3)
                    with dl1:
                        st.download_button(
                            "📄 Lesson (.md)",
                            lesson_text,
                            file_name=f"{m.name}_lesson.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )
                    with dl2:
                        if quiz_file.exists():
                            st.download_button(
                                "❓ Quiz (.json)",
                                quiz_file.read_text(encoding="utf-8"),
                                file_name=f"{m.name}_quiz.json",
                                mime="application/json",
                                use_container_width=True,
                            )
                    with dl3:
                        if visual_file.exists():
                            st.download_button(
                                "🎨 Visuals (.md)",
                                visual_file.read_text(encoding="utf-8"),
                                file_name=f"{m.name}_visuals.md",
                                mime="text/markdown",
                                use_container_width=True,
                            )

# ── Tab 3: Interactive Quiz ────────────────────────────────────────
with tab_quiz:
    modules_with_quiz = [m for m in sorted(MODULES_DIR.glob("module_*")) if (m / "quiz.json").exists()]

    if not modules_with_quiz:
        st.info("No quizzes available yet. Generate some modules first.")
    else:
        # Module selector
        module_names = {}
        for m in modules_with_quiz:
            lf = m / "lesson.md"
            if lf.exists():
                t = lf.read_text(encoding="utf-8").split("\n")[0].replace("#", "").strip()
            else:
                t = m.name
            module_names[t] = m

        chosen_title = st.selectbox("Select a module to quiz yourself on:", list(module_names.keys()))
        chosen_module = module_names[chosen_title]

        try:
            quiz_data = json.loads((chosen_module / "quiz.json").read_text(encoding="utf-8"))
        except Exception:
            quiz_data = []

        if not quiz_data or not isinstance(quiz_data, list):
            st.warning("Quiz data is unavailable or malformed for this module.")
        else:
            st.markdown(f"### ❓ Quiz: {chosen_title}")
            st.caption(f"{len(quiz_data)} questions")
            st.markdown("")

            # Initialize session state for this module
            key_prefix = f"quiz_{chosen_module.name}"
            if f"{key_prefix}_answers" not in st.session_state:
                st.session_state[f"{key_prefix}_answers"] = {}
            if f"{key_prefix}_submitted" not in st.session_state:
                st.session_state[f"{key_prefix}_submitted"] = False

            answers = st.session_state[f"{key_prefix}_answers"]
            submitted = st.session_state[f"{key_prefix}_submitted"]

            with st.form(f"quiz_form_{chosen_module.name}"):
                for i, q in enumerate(quiz_data):
                    question_text = q.get("question", f"Question {i+1}")
                    options = q.get("options", [])

                    st.markdown(f'<div class="quiz-question"><p>Q{i+1}. {question_text}</p></div>', unsafe_allow_html=True)

                    choice = st.radio(
                        f"q{i}",
                        options,
                        index=None,
                        key=f"{key_prefix}_q{i}",
                        label_visibility="collapsed",
                    )
                    answers[i] = choice

                submitted_btn = st.form_submit_button("✅ Submit Quiz", type="primary", use_container_width=True)
                if submitted_btn:
                    st.session_state[f"{key_prefix}_submitted"] = True
                    st.session_state[f"{key_prefix}_answers"] = answers
                    st.rerun()

            if st.session_state.get(f"{key_prefix}_submitted"):
                st.markdown("---")
                st.markdown("### 📊 Results")
                score = 0
                for i, q in enumerate(quiz_data):
                    user_ans = answers.get(i)
                    correct_letter = q.get("correct_option", "")
                    options = q.get("options", [])

                    # Match correct option — could be "A", "A.", or the full text
                    correct_full = next((o for o in options if o.startswith(correct_letter)), correct_letter)
                    is_correct = user_ans and (user_ans == correct_full or user_ans.startswith(correct_letter))
                    if is_correct:
                        score += 1

                    icon = "✅" if is_correct else "❌"
                    st.markdown(f"{icon} **Q{i+1}.** {q.get('question', '')}")
                    if not is_correct and user_ans:
                        st.markdown(f"  - Your answer: `{user_ans}`")
                        st.markdown(f"  - Correct answer: `{correct_full}`")
                    if q.get("explanation"):
                        st.caption(f"💡 {q['explanation']}")

                pct = int(score / len(quiz_data) * 100)
                st.markdown(f"### Score: **{score}/{len(quiz_data)}** ({pct}%)")
                if pct == 100:
                    st.success("🎉 Perfect score! Excellent work!")
                    st.balloons()
                elif pct >= 60:
                    st.info("👍 Good job! Review the missed questions above.")
                else:
                    st.warning("📚 Keep studying! Review the lesson and try again.")

                if st.button("🔄 Retake Quiz"):
                    del st.session_state[f"{key_prefix}_answers"]
                    del st.session_state[f"{key_prefix}_submitted"]
                    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────
st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center; color:#374151; font-size:0.83rem;">'
    '🏥 AI Healthcare Training Generator &nbsp;|&nbsp; Powered by Google Gemini AI</p>',
    unsafe_allow_html=True,
)

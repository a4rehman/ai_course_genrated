# src/generate_modules.py
"""Generate healthcare training modules using Google Gemini.

This script reads a configuration file defining each module's topic and calls the Gemini API
to produce lesson content, quizzes, and visual guidance.
"""

import os
import json
import pathlib
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("Gemini_API_Key")
if not GEMINI_API_KEY:
    raise EnvironmentError("Please set Gemini_API_Key in your .env file.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# -----------------------------------------------------------------------------
# Prompt templates
# -----------------------------------------------------------------------------
PROMPT_FILE = pathlib.Path(__file__).parent.parent / "prompts" / "claude_prompts.json"
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

def call_gemini(system_prompt: str, user_prompt: str) -> str:
    """Send a request to Gemini and return the generated text."""
    # Combine system and user prompt for Gemini if needed, 
    # but Gemini 1.5 Pro/Flash supports system_instruction.
    chat = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_prompt
    )
    response = chat.generate_content(user_prompt)
    return response.text

def generate_module(module_id: int, topic: str) -> None:
    module_dir = pathlib.Path("modules") / f"module_{module_id}"
    (module_dir / "html").mkdir(parents=True, exist_ok=True)

    print(f"  > Generating lesson...")
    lesson_text = call_gemini(PROMPTS["lesson"]["system"], PROMPTS["lesson"]["user"].format(topic=topic))
    (module_dir / "lesson.md").write_text(lesson_text, encoding="utf-8")

    print(f"  > Generating quiz...")
    quiz_json_str = call_gemini(PROMPTS["quiz"]["system"], PROMPTS["quiz"]["user"].format(topic=topic))
    # Clean up JSON if Gemini adds markdown code blocks
    quiz_json_str = quiz_json_str.replace("```json", "").replace("```", "").strip()
    try:
        quiz_data = json.loads(quiz_json_str)
    except json.JSONDecodeError:
        quiz_data = {"raw": quiz_json_str}
    (module_dir / "quiz.json").write_text(json.dumps(quiz_data, indent=2), encoding="utf-8")

    print(f"  > Generating visuals...")
    visual_md = call_gemini(PROMPTS["visual"]["system"], PROMPTS["visual"]["user"].format(topic=topic))
    (module_dir / "visual.md").write_text(visual_md, encoding="utf-8")

    # Render HTML
    template_path = pathlib.Path("html") / "module_template.html"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
        html_content = template.replace("{{topic}}", topic)
        html_content = html_content.replace("{{lesson_content_html}}", lesson_text) # Simple for now
        html_content = html_content.replace("{{quiz_data}}", json.dumps(quiz_data))
        (module_dir / "html" / "lesson.html").write_text(html_content, encoding="utf-8")

    # History
    history_path = pathlib.Path("prompts") / "prompt_history.json"
    history = []
    if history_path.exists():
        try: history = json.loads(history_path.read_text(encoding="utf-8"))
        except: pass
    history.append({"module_id": module_id, "topic": topic, "model": "gemini-1.5-flash"})
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

def main() -> None:
    config = [
        "Family Caregiver Training",
        "Handwashing and Glove Use in Personal Care",
        "Introduction to Cultural and Diversity Training",
        "Personal Care Worker (PCW) Foundations Training",
        "Trauma-Informed & Culturally Competent Care Training",
        "Community Health Worker Training",
    ]
    for i, topic in enumerate(config, start=1):
        print(f"Generating module {i}: {topic}")
        generate_module(i, topic)
    print("All modules generated successfully.")

if __name__ == "__main__":
    main()

# src/generate_modules.py
"""Generate healthcare training modules using Anthropic Claude.

This script reads a configuration file defining each module's topic and calls the Claude API
to produce:
  - lesson markdown (title, objectives, script, takeaways, deeper dive)
  - quiz JSON
  - visual guidance markdown
  - HTML lesson page (rendered from a Jinja‑like template)

The generated files are stored under `modules/module_<n>/`.
"""

import os
import json
import pathlib
from typing import Dict, Any
import requests

# Load API key from env
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise EnvironmentError("Please set ANTHROPIC_API_KEY environment variable.")

BASE_URL = "https://api.anthropic.com/v1/messages"
HEADERS = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# -----------------------------------------------------------------------------
# Prompt templates (kept in separate JSON files for easy editing)
# -----------------------------------------------------------------------------
PROMPT_FILE = pathlib.Path(__file__).parent.parent / "prompts" / "claude_prompts.json"
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)


def call_claude(system_prompt: str, user_prompt: str) -> str:
    """Send a request to Claude and return the generated text."""
    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 4096,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["content"][0]["text"]


def generate_module(module_id: int, topic: str) -> None:
    module_dir = pathlib.Path("modules") / f"module_{module_id}"
    (module_dir / "html").mkdir(parents=True, exist_ok=True)

    # 1️⃣ Lesson markdown
    lesson_prompt = PROMPTS["lesson"]
    lesson_text = call_claude(
        system_prompt=lesson_prompt["system"],
        user_prompt=lesson_prompt["user"].format(topic=topic),
    )
    (module_dir / "lesson.md").write_text(lesson_text, encoding="utf-8")

    # 2️⃣ Quiz JSON
    quiz_prompt = PROMPTS["quiz"]
    quiz_json_str = call_claude(
        system_prompt=quiz_prompt["system"],
        user_prompt=quiz_prompt["user"].format(topic=topic),
    )
    try:
        quiz_data = json.loads(quiz_json_str)
    except json.JSONDecodeError:
        # fallback – store raw text
        quiz_data = {"raw": quiz_json_str}
    (module_dir / "quiz.json").write_text(json.dumps(quiz_data, indent=2), encoding="utf-8")

    # 3️⃣ Visual guidance markdown
    visual_prompt = PROMPTS["visual"]
    visual_md = call_claude(
        system_prompt=visual_prompt["system"],
        user_prompt=visual_prompt["user"].format(topic=topic),
    )
    (module_dir / "visual.md").write_text(visual_md, encoding="utf-8")

    # 4️⃣ Render HTML using a simple string template (module_template.html)
    template_path = pathlib.Path("html") / "module_template.html"
    template = template_path.read_text(encoding="utf-8")
    # Insert placeholders – the template expects {{lesson_content}} and {{quiz_data}}
    html_content = template.replace("{{lesson_content}}", lesson_text)
    html_content = html_content.replace("{{quiz_data}}", json.dumps(quiz_data))
    (module_dir / "html" / "lesson.html").write_text(html_content, encoding="utf-8")

    # Record prompt usage
    history_path = pathlib.Path("prompts") / "prompt_history.json"
    history = []
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    history.append({
        "module_id": module_id,
        "topic": topic,
        "lesson_prompt": lesson_prompt,
        "quiz_prompt": quiz_prompt,
        "visual_prompt": visual_prompt,
    })
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")


def main() -> None:
    # Configuration: list of module topics (feel free to extend)
    config = [
        "Family Caregiver Training",
        "Handwashing and Glove Use in Personal Care",
        "Introduction to Cultural and Diversity Training",
        "Personal Care Worker (PCW) Foundations Training",
        "Trauma‑Informed & Culturally Competent Care Training",
        "Community Health Worker Training",
    ]
    for i, topic in enumerate(config, start=1):
        print(f"Generating module {i}: {topic}")
        generate_module(i, topic)
    print("All modules generated.")

if __name__ == "__main__":
    main()

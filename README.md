# AI‑Assisted Healthcare Training Course Generator

This repository contains a complete system for generating beginner‑friendly, professional training modules for healthcare and caregiving topics using **Anthropic Claude**.

## Folder Structure
```
training_project/
│
├── modules/                # Generated lesson content per module
│   ├── module_1/
│   │   ├── lesson.md       # Lesson script, objectives, takeaways, etc.
│   │   ├── quiz.json       # Quiz questions & answers
│   │   ├── visual.md       # Visual guidance (slide text, icons, animations)
│   │   └── html/           # Rendered HTML page for this module
│   └── ... (module_2 … module_6)
│
├── prompts/                # Claude prompt templates & history
│   ├── claude_prompts.json
│   ├── followup_prompts.json
│   └── prompt_history.json
│
├── html/                   # Front‑end assets
│   ├── index.html          # Homepage / module navigator
│   ├── module_template.html# Re‑usable HTML for each lesson
│   ├── styles.css
│   └── script.js
│
├── src/                    # Generation scripts (Python)
│   └── generate_modules.py # Calls Claude API to create module files
│
├── docs/                   # Editable output documents
│   ├── editable_scripts.docx
│   └── training_outline.pdf
│
└── assets/                 # Icons, illustrations, quiz graphics
    ├── icons/
    ├── illustrations/
    └── quiz_assets/
```

## Quick Start
1. Install Python dependencies (`anthropic`, `requests`).
2. Set your Claude API key in an environment variable `ANTHROPIC_API_KEY`.
3. Run `python src/generate_modules.py` – it will populate the `modules/` directory and update `prompt_history.json`.
4. Open `html/index.html` in a browser to explore the generated lessons.

The system is designed for extensibility – add new modules by updating `module_config.json` and re‑run the generator.

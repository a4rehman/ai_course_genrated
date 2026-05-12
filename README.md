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

## Deployment & Usage

### 🚀 Run on Streamlit (Live Demo)
This project is ready to be deployed on **Streamlit Cloud**:
1. Push this repository to GitHub (Done).
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect this repository.
3. In the Streamlit App settings, add your `ANTHROPIC_API_KEY` to **Secrets** or enter it directly in the app sidebar.
4. The app will allow you to generate modules, preview them, and manage the training suite from a beautiful web interface.

### 💻 Local Development
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Setup Environment**:
   Create a `.env` file with `ANTHROPIC_API_KEY=your_key_here`.
3. **Run Streamlit**:
   ```bash
   streamlit run streamlit_app.py
   ```
4. **CLI Generation** (Optional):
   ```bash
   python src/generate_modules.py
   ```

## Folder Structure
- `streamlit_app.py`: Main interactive dashboard.
- `src/generate_modules.py`: Core logic for calling Claude API.
- `prompts/`: System and user prompt templates.
- `html/`: UI templates and styles for the generated lessons.
- `modules/`: (Generated) Contains the training content for each topic.
- `assets/` & `docs/`: Placeholders for icons, illustrations, and exported documents.

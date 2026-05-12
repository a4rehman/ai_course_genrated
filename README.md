# AI‑Assisted Healthcare Training Course Generator (Gemini Edition)

This repository contains a complete system for generating beginner‑friendly, professional training modules for healthcare and caregiving topics using **Google Gemini 1.5 Flash**.

## Features
- **Powered by Gemini**: High-speed, high-quality content generation using Google's latest models.
- **Dynamic Training Dashboard**: Interactive HTML/CSS training pages.
- **Interactive Quizzes**: Auto-generated scenario-based assessments.
- **Streamlit Console**: Easy-to-use web interface for content management.

## Deployment & Usage

### 🚀 Run on Streamlit (Live Demo)
This project is ready to be deployed on **Streamlit Cloud**:
1. Push this repository to GitHub (Done).
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect this repository.
3. In the Streamlit App settings, add your `Gemini_API_Key` to **Secrets** or enter it directly in the app sidebar.
4. The app will allow you to generate modules, preview them, and manage the training suite from a beautiful web interface.

### 💻 Local Development
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Setup Environment**:
   Create a `.env` file with `Gemini_API_Key=your_key_here`.
3. **Run Streamlit**:
   ```bash
   streamlit run streamlit_app.py
   ```
4. **CLI Generation** (Optional):
   ```bash
   python src/generate_modules.py
   ```

## Folder Structure
```
.
├── modules/                # Generated lesson content per module
├── prompts/                # Prompt templates & history
├── html/                   # Front‑end assets
├── src/                    # Generation scripts (Python)
├── streamlit_app.py        # Streamlit dashboard
├── requirements.txt        # Python dependencies
└── .env                    # API Key configuration
```

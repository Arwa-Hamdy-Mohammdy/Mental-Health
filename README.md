# 🧠 AI Mental Health Companion — MindCare AI

An AI-powered mental-health companion designed to provide evidence-based mental-health information, emotional support, and wellness exercises through natural language interaction.

Built with **LLM + RAG + LangChain + Conversation Memory + Pydantic Output Parser + Safety Layer + Streamlit + FastAPI + ngrok**.

---

## 🌟 Key Features

1. **Jupyter Notebook Workflows (`mindcare_ai_companion.ipynb`)**:
   - Structured step-by-step cells covering Milestones 1 through 16.
2. **Retrieval-Augmented Generation (RAG)**:
   - Queries curated mental-health knowledge bases on stress, anxiety, sleep hygiene, and mindfulness.
3. **Pydantic Structured Output**:
   - Outputs JSON containing: `response`, `topic`, `suggested_activity`, `sources`, `safety_level`.
4. **Safety Layer & Crisis Routing**:
   - Automatically detects high-risk self-harm triggers and immediately provides crisis hotline support.
5. **Interactive Streamlit Web UI (`app.py`)**:
   - 💬 AI Chat Interface with Memory
   - 📊 Mood Tracker & Insights Log
   - 📝 Daily Reflection Journal
   - 🧘 Interactive Breathing (4-7-8) & Grounding (5-4-3-2-1) Exercises
   - 📚 Searchable Knowledge Base
   - 🚨 Emergency Crisis Resources
6. **Lightweight FastAPI Backend (`api.py`)**:
   - `POST /chat` endpoint returning structured JSON payload for mobile/web integration.

---

## 🚀 How to Run

### 1. Run the Jupyter Notebook
Open VS Code or Jupyter Lab:
```bash
jupyter notebook mindcare_ai_companion.ipynb
```
Run the notebook cells sequentially to experience each milestone of the AI pipeline.

---

### 2. Launch the Streamlit Web Application
Run the command below:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

### 3. Launch the FastAPI Backend (Optional)
```bash
python api.py
```
Or with Uvicorn:
```bash
uvicorn api:app --reload --port 8000
```
Interactive API documentation will be available at `http://127.0.0.1:8000/docs`.

---

### 4. Expose via ngrok Demo (Optional)
To create a public demonstration link:
```bash
ngrok http 8501
# Or for FastAPI backend:
ngrok http 8000
```

---

## 📁 Project Structure

```
Mental Health/
├── data/
│   └── knowledge_base/        # Educational markdown knowledge base files
│       ├── stress_management.md
│       ├── anxiety_and_coping.md
│       ├── sleep_hygiene.md
│       ├── mindfulness_and_wellness.md
│       └── emergency_and_resources.md
├── src/                       # Core AI Engine package
│   ├── __init__.py
│   ├── config.py              # Configuration constants & crisis hotlines
│   ├── safety.py              # High-risk evaluation & safety protocol
│   ├── rag_pipeline.py        # Chunking, TF-IDF / Embedding search
│   ├── llm_chain.py           # Prompting, memory & Intent-Aware logic
│   ├── database.py            # SQLite User Authentication & Chat History
│   └── mood_tracker.py        # Mood tracking & journal logging
├── docs/                      # Documentation & Jupyter Notebooks
│   └── mindcare_ai_companion.ipynb
├── tests/                     # Automated Test Suite
│   ├── test_auth.py           # Authentication & User persistence tests
│   ├── test_pipeline.py      # End-to-end RAG & Intent detector tests
│   └── test_repeating_fix.py  # Response repetition fix verification
├── app.py                     # Streamlit frontend UI
├── api.py                     # FastAPI REST server with Auth & Persistence
├── requirements.txt           # Dependency file
└── README.md                  # Project documentation
```

# 🧠 MindCare AI — AI Mental Health Companion
## Project Presentation (8 Slides)

---

### 📌 Slide 1: Project Overview & Vision (العنوان والمقدمة العامة)
**Title:** MindCare AI — Intent-Aware & Context-Grounded Mental Health Companion

* **Vision:** An AI-powered conversational platform designed to provide evidence-based mental health education, empathetic emotional support, mood tracking, and interactive wellness exercises.
* **Core Philosophy:** Bridges the gap between general AI chatbots and clinical safety by using **Intent Detection**, **Retrieval-Augmented Generation (RAG)**, and **Strict Safety Guardrails**.
* **Target Audience:** Individuals seeking daily emotional support, stress management tools, mindfulness guidance, and mental wellness tracking.
* **Disclaimer:** Designed for support and education—does not replace licensed clinical therapy or medical diagnosis.

---

### 📌 Slide 2: Problem Statement & Main Objectives (المشكلة والهدف الرئيسي)
**Title:** Why MindCare AI?

* **The Problem:**
  1. Traditional LLM chatbots often suffer from **hallucinations** or provide generic, unverified medical advice.
  2. Lack of **emotional sensitivity** and strict safety controls during user crisis moments.
  3. Absence of integrated tools for daily self-reflection, mood tracking, and grounding exercises in a single application.

* **Project Objectives:**
  1. **Ground Responses:** Provide verified information from curated clinical knowledge bases (CBT, Sleep Hygiene, Mindfulness).
  2. **Smart Intent Awareness:** Differentiate between casual venting (requiring empathy) and information requests (requiring structured RAG retrieval).
  3. **Ensure Safety:** Instantly intercept self-harm or crisis triggers and present official hotline resources.
  4. **Provide Holistic Wellness:** Integrate interactive exercises, mood analytics, and persistent user journals.

---

### 📌 Slide 3: System Architecture & Workflow (المعمارية وسير العمل)
**Title:** How MindCare AI Works (End-to-End Flow)

* **Pipeline Flow:**
  1. **Input Evaluation:** User sends a query through Streamlit UI or FastAPI endpoint.
  2. **Safety Layer Check:** Scans message for crisis / self-harm triggers. If high-risk, immediate emergency response is triggered.
  3. **Intent Detection:** Classifies intent as either `Casual Emotional Venting` or `Information Request`.
  4. **Dynamic Context Processing:**
     - *Casual Venting:* Routed directly to LLM with conversation memory for warm, empathetic dialogue.
     - *Information Request:* Routed to RAG retriever (FAISS + SentenceTransformers) to fetch exact knowledge base context.
  5. **Structured Output Parsing:** Output is parsed via Pydantic Schema (`response`, `topic`, `suggested_activity`, `sources`).

---

### 📌 Slide 4: Key Features & User Capabilities (المميزات الرئيسية والتفاعلية)
**Title:** Core Features & Interactive Tools

1. **💬 Conversational Companion:**
   * Context-aware chat with memory of past interactions.
   * Empathetic responses tailored to emotional state.

2. **📊 Mood Tracker & Analytics:**
   * Log daily moods, stress levels (1-10), and sleep hours.
   * Visual trend analytics for tracking mental wellness over time.

3. **📝 Daily Reflection Journal:**
   * Secure, private space for personal journal entries with mood tagging.

4. **🧘 Interactive Wellness Exercises:**
   * **4-7-8 Breathing Technique:** Guided visual animation timer for relaxation.
   * **5-4-3-2-1 Grounding Technique:** Interactive sensory check-in for anxiety reduction.

5. **🔐 User Authentication & History Persistence:**
   * SQLite database backend with encrypted passwords (`bcrypt`) and full chat history retention.

---

### 📌 Slide 5: RAG & Knowledge Base Engine (محرك البحث والاسترجاع RAG)
**Title:** Retrieval-Augmented Generation (RAG) Architecture

* **Curated Knowledge Base:**
  * Custom markdown documents covering: *Stress Management*, *Anxiety & Coping*, *Sleep Hygiene*, *Mindfulness & Wellness*, and *Emergency Resources*.
* **Document Processing & Chunking:**
  * Recursive character text splitting for optimal context windowing.
* **Vector Indexing & Embedding:**
  * Powered by `SentenceTransformers` (`all-MiniLM-L6-v2`) and `FAISS` vector store.
  * Fallback similarity engine using `Scikit-Learn` TF-IDF for rapid CPU execution.
* **Benefits:**
  * 0% Hallucination on factual wellness techniques.
  * Exact citation of sources provided alongside responses.

---

### 📌 Slide 6: Safety Layer & Crisis Protocols (طبقة الأمان والتعامل مع الأزمات)
**Title:** Safety-First AI Design

* **Crisis Keywords Interception:**
  * Real-time regex and semantic match for expressions of self-harm, suicidal ideation, or severe panic.
* **Immediate Intervention Protocol:**
  * Bypass normal LLM generation when risk is detected.
  * Return compassionate crisis message + direct contact numbers for global & local emergency hotlines (e.g., Egypt Secretariat of Mental Health `08008880700` / `16328`).
* **Ethical Guardrails:**
  * Clear boundaries stating AI limitations and encouraging professional medical consultation when necessary.

---

### 📌 Slide 7: Tech Stack & Tools (التقنيات والمكتبات المستخدمة)
**Title:** Technologies & Frameworks Used

| Layer | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core development language |
| **AI Orchestration** | LangChain | LLM prompts, chains, memory, and RAG pipeline |
| **Embeddings & Vector DB** | SentenceTransformers + FAISS | High-dimensional semantic search |
| **Output Structuring** | Pydantic v2 | Schema validation & structured JSON outputs |
| **Backend API** | FastAPI + SQLite + bcrypt | User Auth, REST API endpoints & persistent DB |
| **Frontend UI** | Streamlit | Modern glassmorphism web interface |
| **Tunneling** | PyNgrok | Public URL exposure for live demonstrations |
| **Workflow** | Jupyter Notebook (`.ipynb`) | 16-Milestone step-by-step pipeline demonstration |

---

### 📌 Slide 8: Future Roadmap & Conclusion (الرؤية المستقبلية والخاتمة)
**Title:** Future Enhancements & Summary

* **Future Roadmap:**
  1. **Voice Integration:** Speech-to-Text & Text-to-Speech for vocal emotional support.
  2. **Multi-lingual Expansion:** Enhanced Arabic dialect understanding for local Arabic contexts.
  3. **Wearable Syncing:** Connect with smartwatch APIs to correlate sleep/heart-rate data with mood logs.
  4. **Therapist Dashboard:** Optional export feature for summary reports to share with professional therapists.

* **Summary:**
  * **MindCare AI** successfully combines modern AI capabilities (LLMs + RAG) with human-centric wellness tools, maintaining high safety standards, verifiable factual responses, and an intuitive user experience.

import json

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 🧠 AI Mental Health Companion — Intent-Aware & Context-Grounded Architecture\n",
    "\n",
    "Welcome to the updated **MindCare AI** companion notebook!  \n",
    "This notebook breaks down the entire project pipeline into clear, modular **cells** featuring **Intent Detection & Conditional RAG Retrieval**.\n",
    "\n",
    "### Modern Architecture Flow:\n",
    "```\n",
    "                    User Message\n",
    "                         │\n",
    "                    Safety Check\n",
    "                         │\n",
    "                  Intent Detection\n",
    "                         │\n",
    "              ┌──────────┴──────────┐\n",
    "              │                     │\n",
    "       Casual / Emotional       Information Request\n",
    "              │                     │\n",
    "              ↓                     ↓\n",
    "         LLM + Memory          RAG Retriever\n",
    "              │                     │\n",
    "              └──────────┬──────────┘\n",
    "                         │\n",
    "                        LLM\n",
    "                         │\n",
    "                  Output Parser (Pydantic Schema)\n",
    "                         │\n",
    "                      Response\n",
    "```"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "--- \n",
    "## 📌 Milestone 1: Environment Setup & Package Imports"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import glob\n",
    "import json\n",
    "from typing import List, Dict, Any, Optional\n",
    "from pydantic import BaseModel, Field\n",
    "\n",
    "print(\"✅ Standard libraries loaded successfully!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "--- \n",
    "## 📌 Milestone 2 & 3: Knowledge Base Loading & Document Chunking"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "from src.rag_pipeline import MentalHealthRAG\n",
    "\n",
    "rag = MentalHealthRAG()\n",
    "print(f\"📚 Loaded {len(rag.documents)} Knowledge Base documents, indexed into {len(rag.chunks)} chunks.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "--- \n",
    "## 📌 Milestone 4: Intent Detection Engine"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "from src.llm_chain import IntentDetector\n",
    "\n",
    "detector = IntentDetector()\n",
    "\n",
    "test_messages = [\n",
    "    \"I feel tired today.\",\n",
    "    \"What is sleep hygiene and how can it help?\",\n",
    "    \"I had a really hard day at university.\",\n",
    "    \"How do I practice 4-7-8 breathing?\"\n",
    "]\n",
    "\n",
    "for msg in test_messages:\n",
    "    intent = detector.detect_intent(msg)\n",
    "    print(f\"Message: '{msg}' --> Detected Intent: [{intent.upper()}]\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "--- \n",
    "## 📌 Milestone 5: Pydantic Output Parser (Adaptive Schema)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "from src.llm_chain import MentalHealthResponseSchema\n",
    "\n",
    "# Casual venting schema example\n",
    "casual_res = MentalHealthResponseSchema(\n",
    "    response=\"I'm sorry you're feeling tired today. Have you been getting enough rest, or has it been an exhausting day?\",\n",
    "    intent=\"casual_emotional\",\n",
    "    topic=None,\n",
    "    suggested_activity=None,\n",
    "    sources=[],\n",
    "    safety_level=\"normal\"\n",
    ")\n",
    "\n",
    "print(\"💬 Casual Venting JSON Output:\")\n",
    "print(json.dumps(casual_res.model_dump(), indent=2))\n",
    "\n",
    "# Factual info request schema example\n",
    "info_res = MentalHealthResponseSchema(\n",
    "    response=\"Sleep hygiene involves keeping a consistent schedule, optimizing your bedroom environment, and avoiding blue light before bed.\",\n",
    "    intent=\"information_request\",\n",
    "    topic=\"Sleep Hygiene & Relaxation\",\n",
    "    suggested_activity=\"Screen-free Wind Down Routine\",\n",
    "    sources=[\"Sleep Hygiene\"],\n",
    "    safety_level=\"normal\"\n",
    ")\n",
    "\n",
    "print(\"\\n📖 Information Request JSON Output:\")\n",
    "print(json.dumps(info_res.model_dump(), indent=2))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "--- \n",
    "## 📌 Milestone 6: Safety Layer Evaluation"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "from src.safety import SafetyChecker\n",
    "\n",
    "safety = SafetyChecker()\n",
    "is_risk, level, payload = safety.evaluate_input(\"I feel like ending it all\")\n",
    "print(f\"Safety Check Result -> High Risk: {is_risk} | Level: {level}\")\n",
    "if is_risk:\n",
    "    print(\"Crisis Response:\", payload[\"response\"])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "--- \n",
    "## 📌 Milestone 7 - 16: End-to-End Intent-Aware Execution"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "from src.llm_chain import MindCareAssistant\n",
    "\n",
    "assistant = MindCareAssistant(rag_engine=rag)\n",
    "\n",
    "queries = [\n",
    "    \"I feel tired today.\",\n",
    "    \"What is sleep hygiene?\",\n",
    "    \"I'm stressed about exams.\",\n",
    "    \"How can I practice box breathing?\"\n",
    "]\n",
    "\n",
    "for q in queries:\n",
    "    print(\"=\" * 60)\n",
    "    print(f\"👤 USER: {q}\")\n",
    "    res = assistant.generate_response(q)\n",
    "    print(f\"⚡ INTENT DETECTED: {res.intent.upper()}\")\n",
    "    print(f\"💬 RESPONSE: {res.response}\")\n",
    "    if res.topic:\n",
    "        print(f\"🏷️ TOPIC: {res.topic}\")\n",
    "    if res.suggested_activity:\n",
    "        print(f\"🧘 ACTIVITY: {res.suggested_activity}\")\n",
    "    if res.sources:\n",
    "        print(f\"📚 SOURCES: {', '.join(res.sources)}\")\n",
    "    print(\"=\" * 60 + \"\\n\")"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

with open("mindcare_ai_companion.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1)

print("Updated Notebook generated successfully!")

"""
LangChain Orchestration Module — Intent-Aware & Context-Grounded Architecture
Handles Safety Checks, Intent Detection (Casual/Emotional vs Information Request),
RAG Retrieval on-demand, Conversation Memory, and Pydantic Output Parsing.
"""

import json
import random
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.safety import safety_evaluator
from src.rag_pipeline import MentalHealthRAG

# Pydantic Schema for Structured Output
class MentalHealthResponseSchema(BaseModel):
    response: str = Field(description="The main response text.")
    intent: str = Field(description="Detected intent: 'casual_emotional', 'information_request', or 'high_risk'.")
    topic: Optional[str] = Field(default=None, description="Primary mental health topic if information requested, else None.")
    suggested_activity: Optional[str] = Field(default=None, description="Practical exercise if applicable/requested, else None.")
    sources: List[str] = Field(default_factory=list, description="Knowledge base sources if RAG retrieved, else empty list.")
    safety_level: str = Field(default="normal", description="Safety status: 'normal' or 'high_risk'.")

class ConversationMemory:
    """Manages chat history and conversational memory for session context."""
    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add_user_message(self, message: str):
        self.history.append({"role": "user", "content": message})

    def add_ai_message(self, message: str):
        self.history.append({"role": "assistant", "content": message})

    def get_formatted_history(self, max_messages: int = 6) -> str:
        recent = self.history[-max_messages:]
        formatted = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "MindCare AI"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

    def get_recent_ai_responses(self, count: int = 3) -> List[str]:
        return [msg["content"] for msg in self.history if msg["role"] == "assistant"][-count:]

    def clear(self):
        self.history = []

class IntentDetector:
    """
    Classifies user message intent:
    - 'information_request': User is explicitly asking for factual info, advice, techniques, or how-to explanations.
    - 'casual_emotional': User is venting, sharing a feeling, greeting, or making a brief statement.
    """
    INFO_TRIGGER_WORDS = [
        "what", "how", "why", "explain", "tips", "ways to", "techniques", "methods",
        "exercise", "strategies", "guide", "info", "information", "help me with",
        "what is", "how do i", "how to", "should i", "benefits of", "causes of",
        "ازاي", "ليه", "ايه", "كيف", "طرق", "تمارين", "نصائح"
    ]

    def detect_intent(self, message: str) -> str:
        msg_lower = message.lower().strip()
        
        # Explicit question mark or info request triggers
        if "?" in msg_lower or any(word in msg_lower for word in self.INFO_TRIGGER_WORDS):
            return "information_request"
            
        # Short emotional statements ("I feel tired", "Today was hard", "Hi", "bad", "exhausting")
        return "casual_emotional"

class MindCareAssistant:
    def __init__(self, rag_engine: Optional[MentalHealthRAG] = None):
        self.rag_engine = rag_engine or MentalHealthRAG()
        self.memory = ConversationMemory()
        self.intent_detector = IntentDetector()

    def generate_response(self, user_message: str, mood_info: Optional[Dict[str, Any]] = None) -> MentalHealthResponseSchema:
        """
        Orchestrates the Intent-Aware AI Pipeline:
        1. Safety Check (High-risk trigger check)
        2. Intent Detection ('casual_emotional' vs 'information_request')
        3. RAG Retrieval (Executed ONLY if intent is 'information_request')
        4. Dynamic Response Generation (Proportional, natural, non-repetitive)
        5. Structured Output Parsing
        """
        # Step 1: Safety Layer Check
        is_high_risk, safety_level, safety_payload = safety_evaluator.evaluate_input(user_message)
        if is_high_risk:
            payload = {
                "response": safety_payload["response"],
                "intent": "high_risk",
                "topic": safety_payload.get("topic"),
                "suggested_activity": safety_payload.get("suggested_activity"),
                "sources": safety_payload.get("sources", []),
                "safety_level": "high_risk"
            }
            self.memory.add_user_message(user_message)
            self.memory.add_ai_message(payload["response"])
            return MentalHealthResponseSchema(**payload)

        # Step 2: Intent Detection
        intent = self.intent_detector.detect_intent(user_message)

        # Step 3 & 4: Branching Execution based on Intent
        if intent == "casual_emotional":
            response_schema = self._generate_casual_emotional_response(user_message, mood_info)
        else:
            response_schema = self._generate_information_request_response(user_message, mood_info)

        # Step 5: Save to Memory
        self.memory.add_user_message(user_message)
        self.memory.add_ai_message(response_schema.response)

        return response_schema

    def _select_non_repetitive_response(self, candidates: List[str]) -> str:
        """Selects a response candidate that hasn't been used recently to prevent repeating templates."""
        recent_responses = self.memory.get_recent_ai_responses(count=5)
        fresh_candidates = [c for c in candidates if c not in recent_responses]
        if fresh_candidates:
            return random.choice(fresh_candidates)
        return random.choice(candidates)

    def _generate_casual_emotional_response(self, user_message: str, mood_info: Optional[Dict[str, Any]]) -> MentalHealthResponseSchema:
        """Generates a dynamic, empathetic response tailored to the specific emotional cue in user input."""
        msg_clean = user_message.strip().lower()

        # Categorized candidates to provide rich variation and prevent repeating "How has your day been going?"
        if any(w in msg_clean for w in ["exhausting", "exhausted", "tired", "drained", "fatigued", "تعبان", "مرهق"]):
            candidates = [
                "I'm sorry you're feeling so exhausted. Has it been a physically draining day, mentally overwhelming, or a mix of both?",
                "Exhaustion can make even simple tasks feel heavy. Please remember to give yourself permission to rest right now.",
                "That sounds really draining. If you want to talk about what's wearing you down, I'm here to listen."
            ]
        elif any(w in msg_clean for w in ["bad", "awful", "terrible", "horrible", "rough", "sucks", "زفت", "سيء", "مش تمام"]):
            candidates = [
                "I'm really sorry things feel bad right now. What's been the hardest part of your day?",
                "Having a rough time is truly exhausting. Would you like to vent about what happened, or would you prefer a soothing distraction?",
                "I hear you. I'm here with you—feel free to share whatever's making today feel so tough."
            ]
        elif any(w in msg_clean for w in ["stupid", "annoying", "dumb", "useless", "pointless", "frustrating", "angry", "عبط", "مستفز"]):
            candidates = [
                "It's completely understandable to feel frustrated when things feel stupid or unfair. What brought that on?",
                "I hear your frustration. Sometimes venting it out helps clear the air—what's annoying you most right now?",
                "That sounds incredibly aggravating. You don't have to carry that frustration alone; tell me what happened."
            ]
        elif any(w in msg_clean for w in ["sad", "down", "unhappy", "depressed", "crying", "lonely", "حزين", "مكتئب"]):
            candidates = [
                "I hear you. Feeling down makes everything feel heavier. I'm right here if you'd like to share what's on your mind.",
                "I'm sorry you're going through a sad moment. Take your time, there's no rush or pressure here.",
                "Sending warmth your way. It's okay to feel sad sometimes—how can I best support you right now?"
            ]
        elif any(w in msg_clean for w in ["overwhelmed", "stressed", "anxious", "panic", "worried", "scared", "مضغوط", "خايف"]):
            candidates = [
                "It sounds like there's a lot weighing on you. Let's take it one step at a time. What's causing the most stress right now?",
                "Stress can feel overwhelming fast. Would taking a deep, slow breath together help bring some relief?",
                "I'm listening. When anxiety or stress hits, sharing it can lighten the load. Tell me what's on your mind."
            ]
        elif any(w in msg_clean for w in ["hello", "hi", "hey", "greetings", "good morning", "good evening", "أهلا", "مرحبا", "سلام"]):
            candidates = [
                "Hello! I'm glad you're here. How are you feeling today?",
                "Hi there! Welcome. How has your day been treating you so far?",
                "Hey! I'm here and ready to chat. What's on your mind today?"
            ]
        elif any(w in msg_clean for w in ["good", "great", "fine", "okay", "happy", "awesome", "well", "الحمد لله", "تمام", "كويس"]):
            candidates = [
                "I'm really glad to hear that! What made today feel good for you?",
                "That's wonderful! I hope the rest of your day stays just as positive.",
                "Awesome! It's always great to hear things are going well. Anything exciting happening today?"
            ]
        else:
            # Dynamic personalized fallback echoing the user's exact words instead of a repetitive generic string
            candidates = [
                f"I hear you saying '{user_message}'. Would you like to tell me more about what's going on?",
                f"I'm listening closely. What's making you feel '{user_message}' at the moment?",
                f"Thank you for sharing that with me. What would feel most helpful for you right now?"
            ]

        response_text = self._select_non_repetitive_response(candidates)

        return MentalHealthResponseSchema(
            response=response_text,
            intent="casual_emotional",
            topic=None,
            suggested_activity=None,
            sources=[],
            safety_level="normal"
        )

    def _generate_information_request_response(self, user_message: str, mood_info: Optional[Dict[str, Any]]) -> MentalHealthResponseSchema:
        """Runs RAG retrieval and generates a grounded response for explicit info/advice queries."""
        # RAG Retrieval
        retrieved_chunks = self.rag_engine.retrieve(user_message, top_k=3)
        sources_list = list(set([c['title'] for c in retrieved_chunks])) if retrieved_chunks else ["Knowledge Base"]

        msg_lower = user_message.lower()

        # Topic & Exercise selection based on user query
        if any(w in msg_lower for w in ["stress", "exam", "pressure", "work", "busy"]):
            topic = "Stress Management & Coping"
            suggested_act = "4-7-8 Diaphragmatic Breathing"
        elif any(w in msg_lower for w in ["anxious", "anxiety", "panic", "worry", "fear"]):
            topic = "Anxiety & Grounding Techniques"
            suggested_act = "5-4-3-2-1 Sensory Grounding Exercise"
        elif any(w in msg_lower for w in ["sleep", "insomnia", "bed", "night"]):
            topic = "Sleep Hygiene & Relaxation"
            suggested_act = "Screen-free Wind Down Routine"
        else:
            topic = "Mindfulness & Emotional Wellbeing"
            suggested_act = "Mindful Breathing Pause"

        # Build grounded summary from retrieved knowledge
        if retrieved_chunks:
            top_snippet = retrieved_chunks[0]['text'][:250].replace("\n", " ")
            response_text = (
                f"Here is helpful context regarding **{topic}** from our mental health resources:\n\n"
                f"> \"{top_snippet}...\"\n\n"
                f"Key coping strategies include breaking down tasks, keeping a consistent routine, and practicing relaxation techniques."
            )
        else:
            response_text = (
                f"Regarding {topic.lower()}, evidence-based practices recommend pacing yourself, "
                f"practicing deep breathing, and reaching out for support when needed."
            )

        return MentalHealthResponseSchema(
            response=response_text,
            intent="information_request",
            topic=topic,
            suggested_activity=suggested_act,
            sources=sources_list,
            safety_level="normal"
        )

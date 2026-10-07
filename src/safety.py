"""
Safety Layer Module
Checks user input for high-risk flags (e.g., self-harm, suicide risk)
and returns immediate crisis response when necessary.
"""

from typing import Dict, Any, Tuple
from src.config import HIGH_RISK_KEYWORDS, EMERGENCY_CONTACTS

class SafetyChecker:
    def __init__(self, high_risk_keywords=None, emergency_contacts=None):
        self.high_risk_keywords = high_risk_keywords or HIGH_RISK_KEYWORDS
        self.emergency_contacts = emergency_contacts or EMERGENCY_CONTACTS

    def evaluate_input(self, user_message: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates user input message.
        Returns:
            is_high_risk (bool): True if high risk detected
            safety_level (str): 'high_risk' or 'normal'
            safety_payload (dict): Structured safety response if high risk
        """
        clean_text = user_message.lower()
        
        # Check for keyword matches
        detected_keywords = [kw for kw in self.high_risk_keywords if kw in clean_text]
        
        if detected_keywords:
            response_text = (
                "It sounds like you are going through a very painful and overwhelming time. "
                "Your safety and wellbeing are extremely important. "
                "Because I am an AI companion and not a crisis service or medical professional, "
                "I urge you to connect right away with someone who can support you."
            )
            
            safety_payload = {
                "response": response_text,
                "topic": "Crisis Support & Safety Alert",
                "suggested_activity": "Contact Emergency Helpline Immediately",
                "sources": [f"{k}: {v}" for k, v in self.emergency_contacts.items()],
                "safety_level": "high_risk",
                "emergency_contacts": self.emergency_contacts
            }
            return True, "high_risk", safety_payload
            
        return False, "normal", {}

# Singleton helper instance
safety_evaluator = SafetyChecker()

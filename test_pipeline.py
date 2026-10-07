import json
from src.safety import SafetyChecker
from src.rag_pipeline import MentalHealthRAG
from src.llm_chain import MindCareAssistant, IntentDetector

def run_tests():
    print("--- 1. Testing Intent Detection ---")
    detector = IntentDetector()
    assert detector.detect_intent("I feel tired today.") == "casual_emotional"
    assert detector.detect_intent("What is sleep hygiene?") == "information_request"
    print("Intent Detection PASSED.")

    print("\n--- 2. Testing Casual Venting Message ---")
    rag = MentalHealthRAG()
    assistant = MindCareAssistant(rag_engine=rag)
    res_casual = assistant.generate_response("I feel tired today.")
    
    assert res_casual.intent == "casual_emotional"
    assert res_casual.topic is None
    assert res_casual.suggested_activity is None
    assert len(res_casual.sources) == 0
    print(f"Casual message PASSED. Response: '{res_casual.response}'")

    print("\n--- 3. Testing Information Request Message ---")
    res_info = assistant.generate_response("What is sleep hygiene?")
    assert res_info.intent == "information_request"
    assert res_info.topic is not None
    assert res_info.suggested_activity is not None
    assert len(res_info.sources) > 0
    print(f"Info request PASSED. Topic: '{res_info.topic}', Sources: {res_info.sources}")

    print("\nSUCCESS: ALL INTENT-AWARE PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    run_tests()

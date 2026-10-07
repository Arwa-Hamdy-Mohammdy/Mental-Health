import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_chain import MindCareAssistant

def test_no_repeats():
    assistant = MindCareAssistant()
    
    test_inputs = ["exhausting", "bad", "stupid", "exhausting", "bad"]
    responses = []
    
    print("--- Testing AI Responses for Short Emotional Inputs ---")
    for msg in test_inputs:
        resp = assistant.generate_response(user_message=msg)
        print(f"User: '{msg}' -> Bot: '{resp.response}'\n")
        responses.append(resp.response)
    
    # Verify no two consecutive responses are identical
    for i in range(len(responses) - 1):
        assert responses[i] != responses[i+1], f"Duplicate consecutive response found: {responses[i]}"
    
    print("[OK] Test passed! The AI no longer repeats the exact same sentence.")

if __name__ == "__main__":
    test_no_repeats()

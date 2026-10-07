import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "knowledge_base")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "vector_store")

# RAG Parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K_RETRIEVAL = 3

# High Risk Keywords for Safety Layer
HIGH_RISK_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "self harm", "cutting myself", "hurt myself", "hanging myself",
    "overdose", "no reason to live", "better off dead", "end it all"
]

# Emergency Contacts Dictionary
EMERGENCY_CONTACTS = {
    "US / Canada Lifeline": "988 (Call/Text 24/7)",
    "US Crisis Text Line": "Text HOME to 741741",
    "UK Samaritans": "116 123",
    "Egypt Mental Health Hotline": "08008880700 / 0220816831",
    "International Emergency": "Contact local emergency services immediately (911 / 999 / 112 / 123)"
}

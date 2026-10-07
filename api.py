from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from src.llm_chain import MindCareAssistant, MentalHealthResponseSchema
from src.rag_pipeline import MentalHealthRAG
import src.database as db

app = FastAPI(
    title="MindCare AI — FastAPI Backend with Authentication",
    description="Backend API with Email/Password User Authentication, Chat History Persistence, and RAG Pipeline.",
    version="2.0.0"
)

# Initialize RAG & Assistant Engine
rag_engine = MentalHealthRAG()
assistant = MindCareAssistant(rag_engine=rag_engine)

# Request & Response Schemas
class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    mood_info: Optional[Dict[str, Any]] = None

class MoodLogRequest(BaseModel):
    user_id: int
    mood: str
    stress_level: int
    sleep_hours: float
    notes: Optional[str] = ""

class JournalRequest(BaseModel):
    user_id: int
    text: str
    mood_tag: Optional[str] = "Calm"


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "MindCare AI Mental Health Companion API",
        "features": ["User Authentication", "RAG Intent Engine", "Persistent Chat History"],
        "endpoints": [
            "/auth/signup", "/auth/login", "/auth/me/{user_id}",
            "/chat", "/chat/history/{user_id}",
            "/mood", "/journal", "/health"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "knowledge_base_chunks": len(rag_engine.chunks)}


# --- Authentication Endpoints ---

@app.post("/auth/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest):
    if not req.email or "@" not in req.email:
        raise HTTPException(status_code=400, detail="Invalid email format.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
    
    user = db.create_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    return user

@app.post("/auth/login", response_model=UserResponse)
def login(req: LoginRequest):
    user = db.authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return user

@app.get("/auth/me/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


# --- Chat & RAG Endpoints ---

@app.post("/chat", response_model=MentalHealthResponseSchema)
def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")
    
    # Save user message to database if user_id is provided
    if request.user_id:
        db.save_chat_message(request.user_id, "user", request.message)
    
    # Generate AI response using LangChain + RAG
    response = assistant.generate_response(
        user_message=request.message,
        mood_info=request.mood_info
    )
    
    # Save assistant response to database if user_id is provided
    if request.user_id:
        db.save_chat_message(request.user_id, "assistant", response.model_dump())
        
    return response

@app.get("/chat/history/{user_id}")
def get_chat_history(user_id: int):
    history = db.get_user_chat_history(user_id)
    return {"user_id": user_id, "history": history}

@app.delete("/chat/history/{user_id}")
def clear_chat_history(user_id: int):
    db.clear_user_chat_history(user_id)
    return {"message": "Chat history cleared successfully."}


# --- Mood & Journal Endpoints ---

@app.post("/mood")
def log_mood(req: MoodLogRequest):
    db.save_user_mood(req.user_id, req.mood, req.stress_level, req.sleep_hours, req.notes or "")
    return {"status": "success", "message": "Mood logged successfully."}

@app.get("/mood/{user_id}")
def get_moods(user_id: int):
    logs = db.get_user_moods(user_id)
    return {"user_id": user_id, "logs": logs}

@app.post("/journal")
def log_journal(req: JournalRequest):
    db.save_user_journal(req.user_id, req.text, req.mood_tag or "Calm")
    return {"status": "success", "message": "Journal entry saved successfully."}

@app.get("/journal/{user_id}")
def get_journals(user_id: int):
    entries = db.get_user_journals(user_id)
    return {"user_id": user_id, "entries": entries}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

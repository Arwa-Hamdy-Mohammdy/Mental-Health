import streamlit as st
import json
import time
from src.rag_pipeline import MentalHealthRAG
from src.llm_chain import MindCareAssistant
from src.mood_tracker import MoodTracker
from src.config import EMERGENCY_CONTACTS
import src.database as db

# Page Configuration
st.set_page_config(
    page_title="MindCare AI — Your Mental Health Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Glassmorphism & Adaptive Cards
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, .main-title {
        font-family: 'Outfit', sans-serif;
    }

    .topic-pill {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 5px 12px;
        border-radius: 18px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .intent-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #9ca3af;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-bottom: 8px;
    }

    .activity-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 12px 16px;
        border-radius: 8px;
        margin-top: 12px;
        color: #d1fae5;
    }

    .crisis-box {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 18px;
        margin: 12px 0;
        color: #fca5a5;
    }

    .user-welcome-card {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Engine Session State
if "assistant" not in st.session_state:
    with st.spinner("Initializing RAG Knowledge Base & MindCare AI Engine..."):
        st.session_state.rag_engine = MentalHealthRAG()
        st.session_state.assistant = MindCareAssistant(rag_engine=st.session_state.rag_engine)
        st.session_state.mood_tracker = MoodTracker()

if "user" not in st.session_state:
    st.session_state.user = None

def load_user_data(user_id: int):
    """Loads chat history from database into session state."""
    db_history = db.get_user_chat_history(user_id)
    if db_history:
        st.session_state.messages = db_history
    else:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": {
                    "response": "Hello! I'm **MindCare AI**, your mental-health companion. How are you feeling today?",
                    "intent": "casual_emotional",
                    "topic": None,
                    "suggested_activity": None,
                    "sources": [],
                    "safety_level": "normal"
                }
            }
        ]

# Sidebar Authentication & Navigation
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/brain.png", width=70)
    st.title("🧠 MindCare AI")
    st.caption("Intent-Aware Mental Health Companion")
    st.divider()

    # User Authentication Block
    if st.session_state.user is None:
        st.subheader("🔑 Account Access")
        auth_mode = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True)
        
        email_input = st.text_input("Email Address", placeholder="user@example.com")
        password_input = st.text_input("Password", type="password")

        if auth_mode == "Login":
            if st.button("Log In", use_container_width=True, type="primary"):
                if not email_input or not password_input:
                    st.error("Please enter both email and password.")
                else:
                    authenticated_user = db.authenticate_user(email_input, password_input)
                    if authenticated_user:
                        st.session_state.user = authenticated_user
                        load_user_data(authenticated_user["id"])
                        st.success(f"Welcome back, {authenticated_user['email']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
        else:
            if st.button("Sign Up", use_container_width=True, type="primary"):
                if not email_input or not password_input:
                    st.error("Please provide email and password.")
                elif len(password_input) < 6:
                    st.warning("Password should be at least 6 characters.")
                else:
                    new_user = db.create_user(email_input, password_input)
                    if new_user:
                        st.session_state.user = new_user
                        load_user_data(new_user["id"])
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("An account with this email already exists.")
        
        st.divider()
        st.info("💡 Log in to save your chat history, mood logs, and journal entries across sessions.")
        nav_option = "💬 AI Chat"  # Default view when guest
    else:
        st.markdown(f"""
            <div class='user-welcome-card'>
                👤 <b>Logged in as:</b><br/>
                <code>{st.session_state.user['email']}</code>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()
            
        st.divider()
        nav_option = st.radio(
            "Navigate",
            ["💬 AI Chat", "📊 Mood Tracker", "📝 Daily Journal", "🧘 Wellness Exercises", "📚 Knowledge Resources", "🚨 Crisis & Safety Help"],
            index=0
        )
        st.divider()

    st.subheader("⚡ Quick Context")
    current_mood = st.selectbox("Current Mood", ["😊 Happy", "😐 Okay", "😔 Sad", "😰 Anxious", "😫 Overwhelmed"], index=1)
    stress_lvl = st.slider("Stress Level (1-10)", 1, 10, 5)
    sleep_hrs = st.number_input("Sleep Last Night (Hours)", 0.0, 14.0, 7.0, 0.5)


# Page 1: Chat Interface
if nav_option == "💬 AI Chat":
    st.markdown("<h2 class='main-title'>💬 MindCare AI Conversation</h2>", unsafe_allow_html=True)
    if st.session_state.user:
        st.caption(f"Connected as `{st.session_state.user['email']}` — Your chat history is saved securely.")
    else:
        st.caption("Guest Session — Log in from the sidebar to save your chat history permanently.")

    # Initialize messages for guest if needed
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": {
                    "response": "Hello! I'm **MindCare AI**, your mental-health companion. How are you feeling today?",
                    "intent": "casual_emotional",
                    "topic": None,
                    "suggested_activity": None,
                    "sources": [],
                    "safety_level": "normal"
                }
            }
        ]

    # Render Chat Messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            data = msg["content"]
            with st.chat_message("assistant", avatar="🧠"):
                if isinstance(data, dict):
                    intent = data.get("intent", "casual_emotional")
                    
                    if data.get("safety_level") == "high_risk":
                        st.markdown(f"""
                            <div class='crisis-box'>
                                <h3>🚨 Safety & Emergency Support Alert</h3>
                                <p>{data.get('response', '')}</p>
                                <h4>Emergency Helplines:</h4>
                                <ul>
                                    {"".join(f"<li><b>{s}</b></li>" for s in data.get('sources', []))}
                                </ul>
                            </div>
                        """, unsafe_allow_html=True)
                    elif intent == "casual_emotional":
                        st.write(data.get("response", ""))
                    else:  # information_request
                        if data.get("topic"):
                            st.markdown(f"<span class='topic-pill'>🏷️ {data['topic']}</span>", unsafe_allow_html=True)
                        st.write(data.get("response", ""))
                        
                        if data.get("suggested_activity"):
                            st.markdown(f"""
                                <div class='activity-box'>
                                    <b>🧘 Suggested Exercise:</b> {data['suggested_activity']}
                                </div>
                            """, unsafe_allow_html=True)
                            
                        if data.get("sources"):
                            with st.expander("📚 Knowledge Base Sources"):
                                for src in data["sources"]:
                                    st.markdown(f"- `{src}`")
                else:
                    st.write(data)

    # Chat Input Box
    user_prompt = st.chat_input("Share what's on your mind...")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        if st.session_state.user:
            db.save_chat_message(st.session_state.user["id"], "user", user_prompt)

        with st.chat_message("user"):
            st.write(user_prompt)

        mood_payload = {
            "mood": current_mood,
            "stress_level": stress_lvl,
            "sleep_hours": sleep_hrs
        }

        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("Processing intent & generating response..."):
                response_schema = st.session_state.assistant.generate_response(
                    user_message=user_prompt,
                    mood_info=mood_payload
                )
                
                resp_dict = response_schema.model_dump()
                st.session_state.messages.append({"role": "assistant", "content": resp_dict})
                
                if st.session_state.user:
                    db.save_chat_message(st.session_state.user["id"], "assistant", resp_dict)

                st.rerun()

    # Clear Chat History Button
    if st.session_state.user and len(st.session_state.messages) > 1:
        if st.button("🗑️ Clear Chat History"):
            db.clear_user_chat_history(st.session_state.user["id"])
            load_user_data(st.session_state.user["id"])
            st.rerun()

# Page 2: Mood Tracker
elif nav_option == "📊 Mood Tracker":
    st.markdown("<h2 class='main-title'>📊 Mood & Wellness Tracker</h2>", unsafe_allow_html=True)
    st.write("Log your mood, stress levels, and sleep hours to gain personal wellness insights.")
    
    user_id = st.session_state.user["id"] if st.session_state.user else None
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Log Entry")
        with st.form("mood_form"):
            m = st.selectbox("Mood", ["😊 Happy", "😐 Okay", "😔 Sad", "😰 Anxious", "😫 Overwhelmed"])
            s = st.slider("Stress Level", 1, 10, 5)
            sl = st.slider("Sleep (Hours)", 1.0, 12.0, 7.0, 0.5)
            notes = st.text_area("Optional Notes")
            submitted = st.form_submit_button("Save Log")
            if submitted:
                if user_id:
                    db.save_user_mood(user_id, m, s, sl, notes)
                    st.success("Mood entry saved to your account!")
                else:
                    st.session_state.mood_tracker.log_mood(m, s, sl, notes)
                    st.success("Mood entry saved for this session (Log in to save permanently).")

    with col2:
        st.subheader("History & Stats")
        if user_id:
            db_moods = db.get_user_moods(user_id)
            if db_moods:
                total = len(db_moods)
                avg_s = sum(l["stress_level"] for l in db_moods) / total
                avg_sl = sum(l["sleep_hours"] for l in db_moods) / total
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Logs", total)
                c2.metric("Avg Stress", f"{round(avg_s, 1)}/10")
                c3.metric("Avg Sleep", f"{round(avg_sl, 1)} hrs")
                
                st.dataframe(db_moods, use_container_width=True)
            else:
                st.info("No saved mood entries yet.")
        else:
            stats = st.session_state.mood_tracker.get_summary_stats()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Logs", stats["total_logs"])
            c2.metric("Avg Stress", f"{stats['avg_stress']}/10")
            c3.metric("Avg Sleep", f"{stats['avg_sleep']} hrs")
            if st.session_state.mood_tracker.mood_logs:
                st.dataframe(st.session_state.mood_tracker.mood_logs, use_container_width=True)

# Page 3: Journal
elif nav_option == "📝 Daily Journal":
    st.markdown("<h2 class='main-title'>📝 Daily Reflection Journal</h2>", unsafe_allow_html=True)
    user_id = st.session_state.user["id"] if st.session_state.user else None
    
    journal_text = st.text_area("Express your thoughts freely...", height=200)
    tag = st.selectbox("Mood Tag", ["Calm", "Stressed", "Grateful", "Confused", "Hopeful"])
    if st.button("Save Journal Entry"):
        if journal_text.strip():
            if user_id:
                db.save_user_journal(user_id, journal_text, tag)
                st.success("Journal entry saved securely to your account!")
            else:
                st.session_state.mood_tracker.log_journal(journal_text, tag)
                st.success("Journal entry saved for this session (Log in to save permanently).")
            
    if user_id:
        user_journals = db.get_user_journals(user_id)
        if user_journals:
            st.subheader("Past Entries")
            for entry in user_journals:
                st.info(f"**[{entry['created_at']}] Tag: {entry['mood_tag']}**\n\n{entry['text']}")
    elif st.session_state.mood_tracker.journal_entries:
        st.subheader("Past Session Entries")
        for entry in reversed(st.session_state.mood_tracker.journal_entries):
            st.info(f"**[{entry['timestamp']}] Tag: {entry['mood_tag']}**\n\n{entry['text']}")

# Page 4: Exercises
elif nav_option == "🧘 Wellness Exercises":
    st.markdown("<h2 class='main-title'>🧘 Interactive Wellness Exercises</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🫁 4-7-8 Breathing", "🖐️ 5-4-3-2-1 Grounding", "💪 Progressive Muscle Relaxation"])
    
    with tab1:
        st.subheader("4-7-8 Diaphragmatic Breathing")
        st.write("1. **Inhale** quietly through your nose for 4 seconds.")
        st.write("2. **Hold** your breath for 7 seconds.")
        st.write("3. **Exhale** completely through your mouth for 8 seconds.")
        if st.button("Start 1-Minute Breathing Timer"):
            bar = st.progress(0)
            status = st.empty()
            for i in range(60):
                time.sleep(1)
                bar.progress((i + 1) / 60)
                phase = (i % 19)
                if phase < 4:
                    status.info("🫁 Inhale slowly (4s)...")
                elif phase < 11:
                    status.warning("⏸️ Hold breath (7s)...")
                else:
                    status.success("😮‍💨 Exhale fully (8s)...")
            status.success("✨ Great job completing your breathing session!")

    with tab2:
        st.subheader("5-4-3-2-1 Grounding Technique")
        st.write("Bring yourself back to the present moment:")
        st.write("👀 **5 things you see**: Look around your room.")
        st.write("✋ **4 things you can feel**: Your feet on the floor, your shirt against skin.")
        st.write("👂 **3 things you hear**: Fan humming, birds outside, your breath.")
        st.write("👃 **2 things you smell**: Coffee, fresh air.")
        st.write("👅 **1 thing you taste**: Mint, water.")

    with tab3:
        st.subheader("Progressive Muscle Relaxation")
        st.write("Tense each muscle group for 5 seconds, then release completely for 10 seconds.")
        st.write("- **Shoulders**: Raise towards ears, hold, release.")
        st.write("- **Hands**: Clench into tight fists, hold, release.")
        st.write("- **Feet**: Curl toes downward, hold, release.")

# Page 5: Resources
elif nav_option == "📚 Knowledge Resources":
    st.markdown("<h2 class='main-title'>📚 Educational Resources</h2>", unsafe_allow_html=True)
    for doc in st.session_state.rag_engine.documents:
        with st.expander(f"📄 {doc['title']}"):
            st.markdown(doc['content'])

# Page 6: Help & Safety
elif nav_option == "🚨 Crisis & Safety Help":
    st.markdown("<h2 class='main-title'>🚨 Emergency & Crisis Support</h2>", unsafe_allow_html=True)
    st.error("If you are in immediate danger or experiencing a life-threatening crisis, please contact emergency services right away.")
    for name, contact in EMERGENCY_CONTACTS.items():
        st.markdown(f"- **{name}**: `{contact}`")

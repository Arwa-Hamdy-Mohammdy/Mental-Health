"""
Mood Tracker & Daily Journal Module
Stores and computes insights from user mood logs and journal entries.
"""

from typing import List, Dict, Any
from datetime import datetime

class MoodTracker:
    def __init__(self):
        self.mood_logs: List[Dict[str, Any]] = []
        self.journal_entries: List[Dict[str, Any]] = []

    def log_mood(self, mood: str, stress_level: int, sleep_hours: float, notes: str = ""):
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mood": mood,
            "stress_level": stress_level,
            "sleep_hours": sleep_hours,
            "notes": notes
        }
        self.mood_logs.append(log_entry)
        return log_entry

    def log_journal(self, entry_text: str, mood_tag: str = "Neutral"):
        journal_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "text": entry_text,
            "mood_tag": mood_tag
        }
        self.journal_entries.append(journal_entry)
        return journal_entry

    def get_summary_stats(self) -> Dict[str, Any]:
        """Calculates basic statistics from mood history."""
        if not self.mood_logs:
            return {
                "total_logs": 0,
                "avg_stress": 0.0,
                "avg_sleep": 0.0,
                "recent_mood": "None"
            }
            
        total = len(self.mood_logs)
        avg_stress = sum(l["stress_level"] for l in self.mood_logs) / total
        avg_sleep = sum(l["sleep_hours"] for l in self.mood_logs) / total
        recent_mood = self.mood_logs[-1]["mood"]
        
        return {
            "total_logs": total,
            "avg_stress": round(avg_stress, 1),
            "avg_sleep": round(avg_sleep, 1),
            "recent_mood": recent_mood
        }

import sqlite3
import json
import time
import math
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any

class InfiniteEpisodicMemory:
    """
    SQLite-backed Infinite Memory + Lightweight TF-IDF Vector Search + Self-Learning Rule Vault.
    Remembers every command, user preference, and self-healed code pattern forever.
    """
    def __init__(self, db_path: str = "knowledge_vault/jarvais_infinite_memory.db"):
        self.db_file = Path(db_path)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodic_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    user_query TEXT,
                    jarvais_reply TEXT,
                    action_json TEXT,
                    success INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_phrase TEXT UNIQUE,
                    healed_code TEXT,
                    usage_count INTEGER DEFAULT 1,
                    updated_at REAL
                )
            """)
            conn.commit()

    def store_interaction(self, query: str, reply: str, action: str, success: bool = True):
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(
                "INSERT INTO episodic_logs (timestamp, user_query, jarvais_reply, action_json, success) VALUES (?, ?, ?, ?, ?)",
                (time.time(), query, reply, action, 1 if success else 0)
            )
            conn.commit()

    def store_learned_skill(self, trigger_phrase: str, healed_code: str):
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                INSERT INTO learned_skills (trigger_phrase, healed_code, usage_count, updated_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(trigger_phrase) DO UPDATE SET
                    healed_code=excluded.healed_code,
                    usage_count=usage_count + 1,
                    updated_at=excluded.updated_at
            """, (trigger_phrase.lower().strip(), healed_code, time.time()))
            conn.commit()

    def recall_relevant_memories(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_words = Counter(query.lower().split())
        if not query_words:
            return []

        with sqlite3.connect(self.db_file) as conn:
            rows = conn.execute(
                "SELECT user_query, jarvais_reply, action_json FROM episodic_logs ORDER BY id DESC LIMIT 200"
            ).fetchall()

        scored = []
        for u_q, j_r, act in rows:
            doc_words = Counter((u_q + " " + j_r).lower().split())
            overlap = sum(min(query_words[w], doc_words[w]) for w in query_words)
            norm = math.sqrt(sum(v * v for v in query_words.values())) * math.sqrt(sum(v * v for v in doc_words.values()))
            score = overlap / norm if norm > 0 else 0.0
            if score > 0.15:
                scored.append((score, {"past_query": u_q, "past_reply": j_r, "past_action": act}))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def get_learned_skill(self, query: str) -> str:
        q_clean = query.lower().strip()
        with sqlite3.connect(self.db_file) as conn:
            row = conn.execute(
                "SELECT healed_code FROM learned_skills WHERE ? LIKE '%' || trigger_phrase || '%' ORDER BY usage_count DESC LIMIT 1",
                (q_clean,)
            ).fetchone()
            return row[0] if row else ""


class SovereignVoiceEngine:
    """
    Cross-Platform Offline Voice Engine (Android Native TextToSpeech + SpeechRecognizer via PyJnius & Desktop Fallback).
    Speaks Roman Urdu, Urdu, and English responses aloud and listens for voice commands.
    """
    def __init__(self):
        self.voice_enabled = True
        self.android_tts = None
        self._init_android_tts()

    def _init_android_tts(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
            self.android_tts = TextToSpeech(PythonActivity.mActivity, None)
        except Exception:
            self.android_tts = None

    def speak(self, text: str):
        if not self.voice_enabled or not text:
            return
        # Clean markdown/code blocks before speaking aloud so JARVAIS only speaks the conversational part
        import re
        clean_speech = re.sub(r"```.*?```", " Code screen par execute kar diya gaya hai Boss. ", text, flags=re.DOTALL)
        clean_speech = re.sub(r"[*_#`~<>]", "", clean_speech).strip()

        if self.android_tts:
            try:
                self.android_tts.speak(clean_speech, 0, None, "jarvais_utt")
                return
            except Exception:
                pass

        # Termux / Linux / PC fallback
        try:
            import subprocess
            subprocess.Popen(["espeak", "-s", "165", clean_speech], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def trigger_android_voice_listen(self, callback):
        """Triggers native Android Speech-to-Text recognizer intent."""
        try:
            from jnius import autoclass
            Intent = autoclass("android.content.Intent")
            RecognizerIntent = autoclass("android.speech.RecognizerIntent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            intent = Intent(RecognizerIntent.ACTION_RECOGNize_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "JARVAIS Listening Boss...")
            PythonActivity.mActivity.startActivityForResult(intent, 9001)
        except Exception as e:
            callback(f"[Voice Mic Notice]: Use text input or grant mic permission ({e})")

import os
import sqlite3
import re
import emoji
import json
import collections
from datetime import datetime
import numpy as np

class PersonaAnalyzer:
    def __init__(self, db_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "parsed_chat.sqlite"), target_sender="Chitraguptar!! "):
        self.db_path = db_path
        self.target_sender = target_sender
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_messages(self, sender=None):
        cursor = self.conn.cursor()
        if sender:
            cursor.execute("SELECT id, datetime_iso, text FROM messages WHERE sender = ? ORDER BY id ASC", (sender,))
        else:
            cursor.execute("SELECT id, datetime_iso, sender, text FROM messages ORDER BY id ASC")
        return cursor.fetchall()

    def get_conversations(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM conversations ORDER BY id ASC")
        return cursor.fetchall()

    def analyze_message_statistics(self):
        msgs = self.get_messages(self.target_sender)
        total = len(msgs)
        if total == 0:
            return {}

        lengths = []
        words = []
        one_word = 0
        short_replies = 0
        long_messages = 0
        months = collections.defaultdict(int)
        
        longest = ""
        shortest = None

        for msg in msgs:
            text = msg['text']
            lengths.append(len(text))
            
            w = text.split()
            wc = len(w)
            words.append(wc)
            
            if wc == 1:
                one_word += 1
            if wc < 5:
                short_replies += 1
            if wc > 20:
                long_messages += 1

            if len(text) > len(longest):
                longest = text
            if shortest is None or len(text) < len(shortest):
                shortest = text

            try:
                dt = datetime.fromisoformat(msg['datetime_iso'])
                month_key = dt.strftime("%Y-%m")
                months[month_key] += 1
            except Exception:
                pass

        return {
            "total_messages": total,
            "average_length_chars": float(np.mean(lengths)),
            "median_length_chars": float(np.median(lengths)),
            "average_length_words": float(np.mean(words)),
            "median_length_words": float(np.median(words)),
            "shortest_message": shortest,
            "longest_message": longest,
            "one_word_replies_count": one_word,
            "short_replies_count": short_replies,
            "long_messages_count": long_messages,
            "messages_per_month": dict(months)
        }

    def analyze_language_and_words(self):
        msgs = self.get_messages(self.target_sender)
        
        all_words = []
        tanglish_keywords = ["ama", "aama", "illa", "da", "mowne", "molae", "enna", "saptiya", "po", "va", "iruka", "ok", "okay"]
        english_keywords = ["yes", "no", "what", "where", "how", "why", "who", "good", "morning", "night", "love", "miss", "you"]
        
        counts = collections.Counter()
        repeated_chars_count = 0
        questions_count = 0

        for msg in msgs:
            text = msg['text'].lower()
            
            # Count repeated chars like "okayyy"
            if re.search(r'(.)\1{2,}', text):
                repeated_chars_count += 1
                
            if '?' in text:
                questions_count += 1
                
            words = re.findall(r'\b\w+\b', text)
            counts.update(words)
            
        tanglish_count = sum(counts[kw] for kw in tanglish_keywords if kw in counts)
        english_count = sum(counts[kw] for kw in english_keywords if kw in counts)
        
        total_tracked = tanglish_count + english_count
        tanglish_pct = (tanglish_count / total_tracked * 100) if total_tracked > 0 else 0
        english_pct = (english_count / total_tracked * 100) if total_tracked > 0 else 0
        
        return {
            "estimated_tanglish_percentage": tanglish_pct,
            "estimated_english_percentage": english_pct,
            "top_words": counts.most_common(50),
            "repeated_characters_count": repeated_chars_count,
            "questions_count": questions_count,
            "specific_words": {
                "okay": counts["okay"] + counts["ok"],
                "ama": counts["ama"] + counts["aama"],
                "illa": counts["illa"],
                "da": counts["da"],
                "mowne": counts["mowne"],
                "molae": counts["molae"]
            }
        }

    def analyze_emojis(self):
        msgs = self.get_messages(self.target_sender)
        emoji_counts = collections.Counter()
        
        for msg in msgs:
            text = msg['text']
            emojis_in_msg = [c for c in text if c in emoji.EMOJI_DATA]
            emoji_counts.update(emojis_in_msg)
            
        return {
            "top_emojis": emoji_counts.most_common(20),
            "total_emojis_used": sum(emoji_counts.values())
        }

    def analyze_rhythm(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, sender, datetime_iso FROM messages ORDER BY id ASC")
        all_msgs = cursor.fetchall()
        
        consecutive_msgs = []
        current_streak = 0
        
        for i, msg in enumerate(all_msgs):
            if msg['sender'] == self.target_sender:
                current_streak += 1
            else:
                if current_streak > 0:
                    consecutive_msgs.append(current_streak)
                    current_streak = 0
                    
        return {
            "average_consecutive_messages": float(np.mean(consecutive_msgs)) if consecutive_msgs else 0,
            "max_consecutive_messages": max(consecutive_msgs) if consecutive_msgs else 0,
            "single_message_responses": consecutive_msgs.count(1),
            "multi_message_responses": len([x for x in consecutive_msgs if x > 1])
        }

    def run_full_analysis(self):
        return {
            "speaker": self.target_sender,
            "message_statistics": self.analyze_message_statistics(),
            "language": self.analyze_language_and_words(),
            "emoji_profile": self.analyze_emojis(),
            "conversational_rhythm": self.analyze_rhythm()
        }

def load_persona(filepath=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "memories", "persona_profile.json")):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def get_style_instructions(profile):
    if not profile:
        return "Use a casual conversational style."
    
    stats = profile.get('message_statistics', {})
    lang = profile.get('language', {})
    emoji_prof = profile.get('emoji_profile', {})
    
    avg_words = stats.get('average_length_words', 3)
    top_words = [w[0] for w in lang.get('top_words', [])[:5]]
    top_emojis = [e[0] for e in emoji_prof.get('top_emojis', [])[:5]]
    
    instructions = [
        "COMMUNICATION STYLE INSTRUCTIONS:",
        f"- STYLE SIGNAL: Historically, your messages were brief (averaging {avg_words:.1f} words). Generally prefer this historical brevity.",
        "- Naturally vary your response length according to the context of the conversation.",
        "- Use short replies when the conversation historically calls for short replies.",
        "- Allow longer responses when the user asks something complex or emotional. DO NOT artificially shorten meaningful responses.",
        "- Preserve the historical conversational rhythm.",
        "- Do not use perfect grammar or capitalization. Lowercase/informal grammar should be a tendency, not a rigid rule.",
        "- Tamil/Tanglish should be a style tendency, not a mandatory percentage.",
        f"- Your most commonly used words include: {', '.join(top_words)}.",
        f"- Your most commonly used emojis include: {', '.join(top_emojis)}. Use them naturally, not according to a fixed quota.",
        "- Use nicknames contextually, not in every message.",
        "- Match the informal tone of the historical messages, but remember historical style should affect HOW you communicate, while historical memory determines WHAT you can truthfully claim. Never mix these concepts.",
        "- Do NOT simply repeat historical messages. Generate new responses using this style."
    ]
    return "\n".join(instructions)

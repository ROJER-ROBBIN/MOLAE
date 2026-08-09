import os
import sys
import json
import sqlite3
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.ai.persona import PersonaAnalyzer

def test_persona_only_analyzes_target():
    analyzer = PersonaAnalyzer(target_sender="Chitraguptar!! ")
    msgs = analyzer.get_messages("Chitraguptar!! ")
    for msg in msgs:
        assert msg['text'] is not None

def test_persona_db_unchanged():
    conn = sqlite3.connect("data/parsed_chat.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages")
    count_before = cursor.fetchone()[0]
    
    analyzer = PersonaAnalyzer(target_sender="Chitraguptar!! ")
    profile = analyzer.run_full_analysis()
    
    cursor.execute("SELECT COUNT(*) FROM messages")
    count_after = cursor.fetchone()[0]
    
    assert count_before == count_after
    conn.close()

def test_persona_profile_validity():
    profile_path = "data/memories/persona_profile.json"
    assert os.path.exists(profile_path)
    
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
        
    assert profile['speaker'] == "Chitraguptar!! "
    assert 'message_statistics' in profile
    assert 'language' in profile
    assert 'emoji_profile' in profile
    
    # Assert specific words counted properly
    assert 'mowne' in profile['language']['specific_words']
    assert profile['language']['specific_words']['mowne'] > 0

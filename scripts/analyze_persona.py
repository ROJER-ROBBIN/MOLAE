import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.ai.persona import PersonaAnalyzer

def generate_report(profile, output_path):
    report_lines = [
        f"# Persona Analysis Report: {profile['speaker']}",
        "",
        "## 1. Message Statistics",
        f"- **Total Messages:** {profile['message_statistics']['total_messages']}",
        f"- **Average Length (chars):** {profile['message_statistics']['average_length_chars']:.2f}",
        f"- **Median Length (chars):** {profile['message_statistics']['median_length_chars']:.2f}",
        f"- **Average Length (words):** {profile['message_statistics']['average_length_words']:.2f}",
        f"- **Median Length (words):** {profile['message_statistics']['median_length_words']:.2f}",
        f"- **One-word replies:** {profile['message_statistics']['one_word_replies_count']}",
        f"- **Short replies (<5 words):** {profile['message_statistics']['short_replies_count']}",
        f"- **Long messages (>20 words):** {profile['message_statistics']['long_messages_count']}",
        "",
        "## 2. Language & Vocabulary",
        f"- **Questions asked:** {profile['language']['questions_count']}",
        f"- **Messages with repeated chars (e.g. okayyy):** {profile['language']['repeated_characters_count']}",
        "",
        "### Specific Word Frequencies",
    ]
    
    for word, count in profile['language']['specific_words'].items():
        report_lines.append(f"- **{word}:** {count}")
        
    report_lines.extend([
        "",
        "### Top 20 Words"
    ])
    
    for word, count in profile['language']['top_words'][:20]:
        report_lines.append(f"- {word}: {count}")
        
    report_lines.extend([
        "",
        "## 3. Emoji Usage",
        f"- **Total emojis used:** {profile['emoji_profile']['total_emojis_used']}",
        "### Top Emojis"
    ])
    
    for emj, count in profile['emoji_profile']['top_emojis']:
        report_lines.append(f"- {emj} : {count}")
        
    report_lines.extend([
        "",
        "## 4. Conversational Rhythm",
        f"- **Average consecutive messages sent before waiting for reply:** {profile['conversational_rhythm']['average_consecutive_messages']:.2f}",
        f"- **Max consecutive messages:** {profile['conversational_rhythm']['max_consecutive_messages']}",
        f"- **Single message responses:** {profile['conversational_rhythm']['single_message_responses']}",
        f"- **Multi-message responses:** {profile['conversational_rhythm']['multi_message_responses']}",
        "",
        "## 5. Important Limitations",
        "> This profile represents statistical patterns in the provided WhatsApp dataset.",
        "> It does not diagnose psychological states or determine 'true' personality.",
        "> Language detection relies on heuristic keywords and may misclassify heavily abbreviated Tanglish."
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

def analyze():
    print("Initializing PersonaAnalyzer...")
    analyzer = PersonaAnalyzer()
    
    print("Running full analysis (this may take a moment)...")
    profile = analyzer.run_full_analysis()
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "memories")
    os.makedirs(out_dir, exist_ok=True)
    
    json_path = os.path.join(out_dir, "persona_profile.json")
    print(f"Saving JSON profile to {json_path}")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
        
    md_path = os.path.join(out_dir, "persona_report.md")
    print(f"Generating Markdown report at {md_path}")
    generate_report(profile, md_path)
    
    print("Done!")

if __name__ == "__main__":
    analyze()

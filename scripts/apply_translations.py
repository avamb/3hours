#!/usr/bin/env python3
"""
Apply translations from translations_output.json to localization.py
"""
import json
import re
from pathlib import Path

def format_python_dict(data: dict, indent: int = 8) -> str:
    """Format dictionary as Python code with proper indentation"""
    lines = []
    indent_str = " " * indent
    
    for key, value in data.items():
        # Escape quotes and backslashes in value
        if isinstance(value, str):
            # Replace actual newlines with \n
            value = value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
            lines.append(f'{indent_str}"{key}": "{value}",')
        else:
            lines.append(f'{indent_str}"{key}": {repr(value)},')
    
    return "\n".join(lines)


def update_localization_file():
    """Update localization.py with new translations"""
    # Load translations
    translations_file = Path(__file__).parent / "translations_output.json"
    with open(translations_file, "r", encoding="utf-8") as f:
        translations = json.load(f)
    
    # Read current localization.py
    localization_file = Path(__file__).parent.parent / "src" / "utils" / "localization.py"
    with open(localization_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    print("Applying translations to localization.py...")
    print()
    
    # Update SUPPORTED_LANGUAGES
    new_languages = ["ru", "en", "uk", "es", "de", "fr", "pt", "it", "zh", "ja", "he"]
    content = re.sub(
        r'SUPPORTED_LANGUAGES = \[.*?\]',
        f'SUPPORTED_LANGUAGES = {new_languages}',
        content,
        flags=re.DOTALL
    )
    print(f"[OK] Updated SUPPORTED_LANGUAGES: {', '.join(new_languages)}")
    
    # For each new language, add to MENU_TEXTS and SYSTEM_MESSAGES
    for lang_code in ["es", "de", "fr", "pt", "it", "zh", "ja", "he"]:
        lang_name = {
            "es": "Spanish",
            "de": "German",
            "fr": "French",
            "pt": "Portuguese",
            "it": "Italian",
            "zh": "Chinese",
            "ja": "Japanese",
            "he": "Hebrew"
        }[lang_code]
        
        print(f"\nAdding {lang_name} ({lang_code})...")
        
        # Check if language already exists
        if f'    "{lang_code}": {{' in content:
            print(f"  [SKIP] {lang_name} already exists in file")
            continue
        
        # Add to MENU_TEXTS (after "uk" section)
        menu_dict = translations["MENU_TEXTS"][lang_code]
        menu_section = f'''    "{lang_code}": {{
{format_python_dict(menu_dict)}
    }},'''
        
        # Find the position to insert (after "uk" section in MENU_TEXTS)
        menu_texts_match = re.search(r'(MENU_TEXTS = \{.*?"uk": \{.*?\},\n)', content, re.DOTALL)
        if menu_texts_match:
            insert_pos = menu_texts_match.end()
            content = content[:insert_pos] + '\n' + menu_section + content[insert_pos:]
            print(f"  [OK] Added MENU_TEXTS for {lang_name}")
        else:
            print(f"  [ERROR] Could not find insertion point for MENU_TEXTS")
        
        # Add to SYSTEM_MESSAGES (after "uk" section)
        system_dict = translations["SYSTEM_MESSAGES"][lang_code]
        system_section = f'''    "{lang_code}": {{
{format_python_dict(system_dict)}
    }},'''
        
        # Find the position to insert (after "uk" section in SYSTEM_MESSAGES)
        # SYSTEM_MESSAGES starts after MENU_TEXTS
        system_messages_start = content.find('SYSTEM_MESSAGES = {')
        if system_messages_start > 0:
            # Find "uk" section in SYSTEM_MESSAGES
            uk_section_match = re.search(r'"uk": \{.*?\},\n', content[system_messages_start:], re.DOTALL)
            if uk_section_match:
                insert_pos = system_messages_start + uk_section_match.end()
                content = content[:insert_pos] + '\n' + system_section + content[insert_pos:]
                print(f"  [OK] Added SYSTEM_MESSAGES for {lang_name}")
            else:
                print(f"  [ERROR] Could not find UK section in SYSTEM_MESSAGES")
        else:
            print(f"  [ERROR] Could not find SYSTEM_MESSAGES")
    
    # Write updated content
    with open(localization_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print()
    print("="*60)
    print("[OK] localization.py updated successfully!")
    print()
    print("Next steps:")
    print("1. Review the changes: git diff src/utils/localization.py")
    print("2. Test the bot with different languages")
    print("3. Commit the changes")


if __name__ == "__main__":
    update_localization_file()

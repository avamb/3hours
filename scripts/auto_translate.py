#!/usr/bin/env python3
"""
Auto-translate localization keys using GPT-4o-mini
Reads existing RU translations and creates translations for missing languages
"""
import os
import sys
import json
from pathlib import Path
from openai import OpenAI

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Languages to translate to (excluding ru, en, uk which already exist)
TARGET_LANGUAGES = {
    "es": "Spanish",
    "de": "German",
    "fr": "French",
    "pt": "Portuguese",
    "it": "Italian",
    "zh": "Chinese (Simplified)",
    "ja": "Japanese",
    "he": "Hebrew",  # Added as per user request
}

# Language-specific instructions
LANGUAGE_CONTEXT = {
    "es": "Use informal 'tú' form for informal messages and 'usted' for formal messages. Use Latin American Spanish variants when appropriate.",
    "de": "Use 'du' for informal and 'Sie' for formal messages. Use standard High German.",
    "fr": "Use 'tu' for informal and 'vous' for formal messages. Use standard French.",
    "pt": "Use Brazilian Portuguese. Use 'você' for informal and 'o senhor/a senhora' for formal.",
    "it": "Use 'tu' for informal and 'Lei' for formal messages.",
    "zh": "Use Simplified Chinese characters. Keep emojis.",
    "ja": "Use polite Japanese forms. Keep emojis.",
    "he": "Use modern Hebrew. Keep emojis and adjust RTL formatting if needed.",
}


def translate_batch(texts: dict, target_lang: str, lang_name: str, client: OpenAI) -> dict:
    """
    Translate a batch of texts to target language using GPT-4o-mini
    
    Args:
        texts: Dictionary of {key: russian_text}
        target_lang: Target language code (es, de, etc.)
        lang_name: Full language name (Spanish, German, etc.)
        client: OpenAI client instance
        
    Returns:
        Dictionary of {key: translated_text}
    """
    # Prepare batch for translation
    batch_json = json.dumps(texts, ensure_ascii=False, indent=2)
    
    context = LANGUAGE_CONTEXT.get(target_lang, "")
    
    system_prompt = f"""You are a professional translator specializing in Telegram bot interfaces.
Translate the following JSON object from Russian to {lang_name}.

IMPORTANT RULES:
1. Keep ALL emojis exactly as they are
2. Keep ALL HTML tags (<b>, <i>, etc.) exactly as they are
3. Keep ALL placeholders ({{variable}}) exactly as they are
4. Preserve line breaks (\\n) exactly as they are
5. Match the tone: informal messages should be informal, formal should be formal
6. {context}
7. Return ONLY valid JSON with the same keys, no extra text

Example input:
{{"key1": "Привет, {{first_name}}! 👋", "key2": "⚙️ <b>Настройки</b>"}}

Example output:
{{"key1": "Hello, {{first_name}}! 👋", "key2": "⚙️ <b>Settings</b>"}}"""

    user_prompt = f"""Translate this JSON from Russian to {lang_name}:

{batch_json}

Return ONLY the translated JSON, no extra text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent translations
            max_tokens=4000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        # Parse JSON result
        translated = json.loads(result_text)
        
        # Validate all keys are present
        missing_keys = set(texts.keys()) - set(translated.keys())
        if missing_keys:
            print(f"  [WARNING] Missing keys in translation: {missing_keys}")
            for key in missing_keys:
                translated[key] = texts[key]  # Fallback to original
        
        return translated
        
    except json.JSONDecodeError as e:
        print(f"  [ERROR] JSON parse error: {e}")
        print(f"  Response was: {result_text[:200]}...")
        raise
    except Exception as e:
        print(f"  [ERROR] Translation error: {e}")
        raise


def main():
    """Main translation workflow"""
    import argparse
    parser = argparse.ArgumentParser(description="Auto-translate localization keys")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm translation")
    parser.add_argument("--lang", type=str, help="Translate only specific language (e.g., es)")
    args = parser.parse_args()
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    # Import localization module
    from src.utils.localization import MENU_TEXTS, SYSTEM_MESSAGES
    
    print("Auto-translation script starting...")
    print(f"Source: Russian (ru)")
    print(f"Target languages: {', '.join(TARGET_LANGUAGES.keys())}")
    print()
    
    # Count keys
    menu_keys_count = len(MENU_TEXTS["ru"])
    system_keys_count = len(SYSTEM_MESSAGES["ru"])
    total_keys = menu_keys_count + system_keys_count
    
    print(f"Keys to translate per language:")
    print(f"   - MENU_TEXTS: {menu_keys_count} keys")
    print(f"   - SYSTEM_MESSAGES: {system_keys_count} keys")
    print(f"   - Total: {total_keys} keys")
    print()
    
    # Estimate cost (GPT-4o-mini: $0.150/1M input tokens, $0.600/1M output tokens)
    # Rough estimate: ~50 tokens per key input, ~50 tokens per key output
    estimated_input_tokens = total_keys * 50 * len(TARGET_LANGUAGES)
    estimated_output_tokens = total_keys * 50 * len(TARGET_LANGUAGES)
    estimated_cost = (estimated_input_tokens / 1_000_000 * 0.150) + (estimated_output_tokens / 1_000_000 * 0.600)
    
    print(f"Estimated cost: ${estimated_cost:.2f} USD")
    print(f"   (Based on GPT-4o-mini pricing: $0.150/1M input, $0.600/1M output)")
    print()
    
    # Ask for confirmation
    if not args.yes:
        confirmation = input("Continue with translation? (yes/no): ")
        if confirmation.lower() not in ["yes", "y"]:
            print("[CANCELLED] Translation cancelled")
            sys.exit(0)
    else:
        print("Auto-confirming translation (--yes flag)")

    
    print()
    print("="*60)
    
    # Load existing translations if any
    output_file = Path(__file__).parent / "translations_output.json"
    translations_output = {
        "MENU_TEXTS": {},
        "SYSTEM_MESSAGES": {}
    }
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            translations_output = json.load(f)
        print(f"Loaded existing translations from {output_file}")
        print()
    
    # Filter languages if --lang specified
    languages_to_process = TARGET_LANGUAGES
    if args.lang:
        if args.lang not in TARGET_LANGUAGES:
            print(f"[ERROR] Language '{args.lang}' not in TARGET_LANGUAGES")
            sys.exit(1)
        languages_to_process = {args.lang: TARGET_LANGUAGES[args.lang]}
        print(f"Processing only: {args.lang}")
        print()
    
    # Process each language
    for lang_code, lang_name in languages_to_process.items():
        print(f"\nTranslating to {lang_name} ({lang_code})...")
        
        # Skip if already translated
        if lang_code in translations_output.get("MENU_TEXTS", {}) and lang_code in translations_output.get("SYSTEM_MESSAGES", {}):
            print(f"  [SKIP] {lang_name} already translated")
            continue
        
        # Translate MENU_TEXTS
        print(f"  Translating MENU_TEXTS ({menu_keys_count} keys)...")
        menu_translated = translate_batch(
            MENU_TEXTS["ru"],
            lang_code,
            lang_name,
            client
        )
        translations_output["MENU_TEXTS"][lang_code] = menu_translated
        print(f"  [OK] MENU_TEXTS translated")
        
        # Save intermediate result
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(translations_output, f, ensure_ascii=False, indent=2)
        print(f"  [SAVED] Intermediate result")
        
        # Translate SYSTEM_MESSAGES
        print(f"  Translating SYSTEM_MESSAGES ({system_keys_count} keys)...")
        system_translated = translate_batch(
            SYSTEM_MESSAGES["ru"],
            lang_code,
            lang_name,
            client
        )
        translations_output["SYSTEM_MESSAGES"][lang_code] = system_translated
        print(f"  [OK] SYSTEM_MESSAGES translated")
        
        # Save final result for this language
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(translations_output, f, ensure_ascii=False, indent=2)
        print(f"  [SAVED] Final result for {lang_name}")
        
        print(f"[OK] {lang_name} complete!")
    
    # Save translations to JSON file
    output_file = Path(__file__).parent / "translations_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translations_output, f, ensure_ascii=False, indent=2)
    
    print()
    print("="*60)
    print(f"[OK] All translations complete!")
    print(f"Translations saved to: {output_file}")
    print()
    print("Next steps:")
    print("1. Review the translations in translations_output.json")
    print("2. Run apply_translations.py to add them to localization.py")


if __name__ == "__main__":
    main()

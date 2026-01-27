#!/usr/bin/env python3
"""
Check onboarding i18n for all 11 supported languages.
Run: PYTHONPATH=<project_root> python scripts/check_onboarding_i18n.py
"""
import sys

from src.utils.localization import (
    SUPPORTED_LANGUAGES,
    get_language_code,
    get_onboarding_text,
    get_system_message,
)

ONBOARDING_KEYS = [
    "address_informal_button", "address_formal_button",
    "address_informal_confirm", "address_formal_confirm",
    "welcome_with_voice",
    "onboarding_select_gender", "onboarding_select_gender_formal",
    "onboarding_timezone_important", "onboarding_ready_confirm",
    "onboarding_complete",
]
QUESTION_KEYS = [f"question_{i}_{f}" for i in range(1, 9) for f in ("informal", "formal")]


def main() -> int:
    failed = []

    ru_welcome = get_onboarding_text("welcome_with_voice", "ru", first_name="X")
    ru_btn = get_onboarding_text("address_informal_button", "ru")

    for lang in SUPPORTED_LANGUAGES:
        for key in ONBOARDING_KEYS:
            try:
                t = get_onboarding_text(key, lang, first_name="Test") if key == "welcome_with_voice" else get_onboarding_text(key, lang)
            except Exception as e:
                failed.append(f"ONBOARD {lang} {key}: {e}")
                continue
            if not t or not isinstance(t, str):
                failed.append(f"ONBOARD {lang} {key}: empty or not str")

        # Localized (not ru fallback) for non-ru
        if lang != "ru":
            w = get_onboarding_text("welcome_with_voice", lang, first_name="X")
            b = get_onboarding_text("address_informal_button", lang)
            if w == ru_welcome or b == ru_btn:
                failed.append(f"ONBOARD {lang}: welcome or address_informal matches ru (fallback)")

        for key in QUESTION_KEYS:
            try:
                formal = "formal" in key
                t = get_system_message(key, lang, formal=formal)
            except Exception as e:
                failed.append(f"QUESTION {lang} {key}: {e}")
                continue
            if not t or t == key:
                failed.append(f"QUESTION {lang} {key}: empty or fallback key")

    if get_language_code("he-IL") != "he" or get_language_code("") != "ru":
        failed.append("get_language_code normalize")

    if failed:
        for f in failed:
            print(f"FAIL: {f}")
        print(f"\nTotal: {len(failed)} failures")
        return 1
    print("OK: all 11 languages have localized onboarding + questions; normalize OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

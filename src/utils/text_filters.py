"""
Text filters / guardrails for user-facing LLM output.
"""

from __future__ import annotations

import re
from typing import Final


ABROAD_PHRASE_RULE_RU: Final[str] = (
    "Не используй формулировки «за границей», «за границу», «за рубежом», «за рубеж» "
    "(в любом регистре и с любыми пробелами). "
    "Вместо них подбирай нейтральные выражения: "
    "«в другой стране» (если речь о месте) и «в другую страну» (если речь о направлении)."
)

# Rule for forbidden religious and community symbols
FORBIDDEN_SYMBOLS_RULE_RU: Final[str] = (
    "ВАЖНО: Никогда не используй в ответах символы, эмодзи и изображения, связанные с "
    "религиозными конфессиями (кресты, полумесяцы, звёзды Давида, буддийские символы и т.д.) "
    "или ЛГБТ-сообществом (радуга, флаги и т.д.). "
    "Используй только нейтральные позитивные эмодзи: 🌟 ⭐ 💫 ✨ 🌸 🌺 💐 🌷 💝 💖 💗 💕 "
    "🤗 😊 😃 🙂 👍 🎉 🎊 ☀️ 🌤️ 🌈 🍀 🌻 и подобные нейтральные символы."
)

# Forbidden emoji characters to filter from bot responses
# Religious symbols
_RELIGIOUS_EMOJIS = {
    "✝️", "✝", "☦️", "☦", "✡️", "✡", "☪️", "☪", "🕉️", "🕉", "☸️", "☸",
    "🛐", "⛪", "🕌", "🕍", "⛩️", "⛩", "🕋", "🔯", "✴️", "📿", "🙏",
    "👼", "😇", "🧕", "👳", "✞", "☩", "♱", "☥", "卐", "卍", "࿕", "࿖",
}

# LGBT-related flags and symbols
_LGBT_EMOJIS = {
    "🏳️‍🌈", "🏳️‍⚧️", "🏳‍🌈", "🏳‍⚧",
}

# Combined set of all forbidden emojis
FORBIDDEN_EMOJIS: Final[frozenset] = frozenset(_RELIGIOUS_EMOJIS | _LGBT_EMOJIS)

# Matches:
# - "за границей" / "за границу"
# - "за рубежом" / "за рубеж"
# with any whitespace, any case.
_ABROAD_PHRASE_RE = re.compile(
    r"(?iu)\bза\s+(?:границ(?P<case>ей|у)|рубеж(?P<case2>ом)?)\b"
)


def replace_abroad_phrases(text: str) -> str:
    """
    Replace forbidden phrases:
    - "за границей" -> "в другой стране"
    - "за границу" -> "в другую страну"
    Keeps capitalization for sentence-start occurrences.
    """

    def _repl(match: re.Match[str]) -> str:
        case = (match.group("case") or "").lower()
        case2 = (match.group("case2") or "").lower()
        is_location = (case == "ей") or (case2 == "ом")
        replacement = "в другой стране" if is_location else "в другую страну"
        if match.group(0)[:1].isupper():
            replacement = replacement[:1].upper() + replacement[1:]
        return replacement

    return _ABROAD_PHRASE_RE.sub(_repl, text)


def remove_forbidden_emojis(text: str) -> str:
    """
    Remove forbidden religious and LGBT-related emojis from text.
    Returns cleaned text.
    """
    result = text
    for emoji in FORBIDDEN_EMOJIS:
        result = result.replace(emoji, "")
    # Clean up any double spaces that might result
    result = re.sub(r"  +", " ", result)
    return result.strip()


def apply_all_filters(text: str) -> str:
    """
    Apply all text filters to bot response:
    1. Replace abroad phrases
    2. Remove forbidden emojis
    """
    text = replace_abroad_phrases(text)
    text = remove_forbidden_emojis(text)
    return text



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



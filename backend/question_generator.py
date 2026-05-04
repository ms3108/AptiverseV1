"""
Question Generator - Groq API Integration

Generates MCQ aptitude questions using the Groq LLM API.
Returns structured dicts compatible with the Question model.
"""
import os
import json
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Prompt template
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert aptitude question generator for competitive exam preparation.
Generate high-quality Multiple Choice Questions (MCQs) that test conceptual understanding and problem-solving skills.
Always respond with valid JSON only — no markdown, no extra text, no code fences."""

USER_PROMPT_TEMPLATE = """Generate {count} unique {difficulty} difficulty MCQ question(s) on the topic: "{topic}".

Return a JSON array. Each element must have EXACTLY these keys:
- "title": short question title (max 150 chars, no trailing punctuation)
- "description": the full question text (clear, unambiguous)
- "option_a": first option text
- "option_b": second option text
- "option_c": third option text
- "option_d": fourth option text
- "correct_answer": exactly one of "A", "B", "C", or "D"
- "explanation": concise step-by-step solution
- "category": one of "Quants", "Logical", "Linguistics"
- "xp_reward": integer — 10 for Easy, 20 for Medium, 30 for Hard

Rules:
- Questions must be self-contained (no references to external figures/tables)
- All four options must be distinct and plausible
- The explanation must justify the correct answer clearly
- Do NOT include numbering like "1." in the title
- Return ONLY the JSON array, nothing else

Example of a single item:
[
  {{
    "title": "Profit percentage on marked price",
    "description": "A shopkeeper marks a product 40% above cost price and gives a 10% discount. What is the profit percentage?",
    "option_a": "26%",
    "option_b": "28%",
    "option_c": "30%",
    "option_d": "32%",
    "correct_answer": "A",
    "explanation": "Let CP = 100. Marked price = 140. After 10% discount, SP = 140 × 0.9 = 126. Profit = 26%. Hence profit % = 26%.",
    "category": "Quants",
    "xp_reward": 20
  }}
]"""


# ─────────────────────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────────────────────

class GroqQuestionGenerator:
    """Generates MCQ questions using the Groq LLM API."""

    # Preferred models in priority order (fastest/cheapest first)
    MODELS = [
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
    ]

    def __init__(self):
        self._client = None

    def _get_client(self):
        """Lazy-initialise the Groq client."""
        if self._client is not None:
            return self._client

        try:
            from groq import Groq  # imported lazily so startup is unaffected
        except ImportError:
            raise RuntimeError(
                "The 'groq' package is not installed. "
                "Run: pip install groq"
            )

        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY environment variable is not set or is empty."
            )

        self._client = Groq(api_key=api_key)
        return self._client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_single(
        self,
        topic: str,
        difficulty: str,
        count: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Generate `count` MCQ questions for the given topic/difficulty.

        Returns a list of dicts ready to be inserted into the Question model.
        Returns an empty list if generation fails after all model attempts.
        """
        client = self._get_client()
        prompt = USER_PROMPT_TEMPLATE.format(
            count=count,
            difficulty=difficulty,
            topic=topic,
        )

        last_error: Exception | None = None
        for model in self.MODELS:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                )
                raw_text = response.choices[0].message.content or ""
                questions = self._parse_response(raw_text, topic, difficulty)
                if questions:
                    logger.info(
                        "Generated %d question(s) via %s for topic='%s' difficulty='%s'",
                        len(questions), model, topic, difficulty,
                    )
                    return questions
            except Exception as exc:
                logger.warning("Model %s failed: %s", model, exc)
                last_error = exc
                continue

        # All models failed
        if last_error:
            raise last_error
        return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_response(
        self,
        raw: str,
        topic: str,
        difficulty: str,
    ) -> List[Dict[str, Any]]:
        """Parse the LLM text response into a validated list of question dicts."""
        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).strip()

        # Try to extract the JSON array portion
        array_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if array_match:
            cleaned = array_match.group(0)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("JSON parse error: %s\nRaw response: %.500s", exc, raw)
            return []

        if not isinstance(data, list):
            data = [data]

        validated = []
        for idx, item in enumerate(data):
            q = self._validate_item(item, idx, topic, difficulty)
            if q:
                validated.append(q)

        return validated

    def _validate_item(
        self,
        item: Any,
        idx: int,
        topic: str,
        difficulty: str,
    ) -> Dict[str, Any] | None:
        """Validate a single question dict; return None if invalid."""
        if not isinstance(item, dict):
            logger.warning("Question %d is not a dict, skipping.", idx + 1)
            return None

        required = [
            "title", "description",
            "option_a", "option_b", "option_c", "option_d",
            "correct_answer", "explanation", "category",
        ]
        missing = [f for f in required if not item.get(f)]
        if missing:
            logger.warning(
                "Question %d missing required fields: %s — skipping.",
                idx + 1, missing,
            )
            return None

        correct = str(item["correct_answer"]).strip().upper()
        if correct not in ("A", "B", "C", "D"):
            logger.warning(
                "Question %d has invalid correct_answer '%s' — skipping.",
                idx + 1, correct,
            )
            return None

        # Default XP by difficulty if missing / invalid
        xp_defaults = {"easy": 10, "medium": 20, "hard": 30}
        xp = item.get("xp_reward")
        try:
            xp = int(xp)
        except (TypeError, ValueError):
            xp = xp_defaults.get(difficulty.lower(), 10)

        return {
            "title": str(item["title"]).strip()[:200],
            "description": str(item["description"]).strip(),
            "option_a": str(item["option_a"]).strip(),
            "option_b": str(item["option_b"]).strip(),
            "option_c": str(item["option_c"]).strip(),
            "option_d": str(item["option_d"]).strip(),
            "correct_answer": correct,
            "explanation": str(item.get("explanation", "")).strip(),
            "category": str(item.get("category", "Quants")).strip(),
            "topic": topic,
            "difficulty": difficulty,
            "xp_reward": xp,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────────────────────────────────────

_instance: GroqQuestionGenerator | None = None


def get_question_generator() -> GroqQuestionGenerator:
    """Return the shared GroqQuestionGenerator instance."""
    global _instance
    if _instance is None:
        _instance = GroqQuestionGenerator()
    return _instance

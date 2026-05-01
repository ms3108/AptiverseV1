"""
Question Generation using Google Gemini AI
Generates MCQ questions for aptitude/interview preparation
"""
import json
import logging
import os
from typing import List, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generate questions using Gemini AI with validation."""

    def __init__(self, api_key: str = None):
        """Initialize Gemini client."""
        api_key = api_key or os.getenv("GEMINI_API_KEY", "AIzaSyC3O6qDqhIsrSFOnke3vG_ksiayH7Noa4c")
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.generation_config = {
            "temperature": 0.9,
            "response_mime_type": "application/json",
        }

    def generate_single(
        self, topic: str, difficulty: str, count: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Generate questions for a given topic and difficulty.

        Args:
            topic: Topic name (e.g., "Profit and Loss", "Time and Work")
            difficulty: One of "Easy", "Medium", "Hard"
            count: Number of questions to generate (1-5)

        Returns:
            List of validated question dictionaries
        """
        if count < 1 or count > 5:
            count = min(5, max(1, count))

        prompt = self._build_prompt(topic, difficulty, count)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
            )

            response_text = response.text
            questions_data = json.loads(response_text)

            if not isinstance(questions_data, list):
                questions_data = [questions_data]

            validated = []
            for q in questions_data:
                if self._validate_question(q):
                    validated.append(q)
                else:
                    logger.warning(f"Invalid question structure: {q}")

            logger.info(f"Generated {len(validated)}/{len(questions_data)} valid questions for {topic}")
            return validated

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            return []
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return []

    def _build_prompt(self, topic: str, difficulty: str, count: int) -> str:
        """Build the prompt for Gemini."""
        return f"""Generate {count} multiple-choice questions for aptitude/interview preparation.

Topic: {topic}
Difficulty: {difficulty}

Return ONLY a valid JSON array with exactly {count} questions. Each question must have:
- title: String (brief title, 5-100 chars)
- description: String (full question text, 10-500 chars)
- category: String (one of: "Quants", "Logical", "Language")
- difficulty: String (exactly "{difficulty}")
- topic: String (exactly "{topic}")
- option_a: String (first option)
- option_b: String (second option)
- option_c: String (third option)
- option_d: String (fourth option)
- correct_answer: String (exactly one of: A, B, C, D)
- explanation: String (why this is correct, 20-500 chars)
- xp_reward: Integer (between 5 and 50)

Example format:
[{{
  "title": "Profit Margin Calculation",
  "description": "A shopkeeper buys goods for Rs. 100 and sells them for Rs. 150. What is the profit percentage?",
  "category": "Quants",
  "difficulty": "{difficulty}",
  "topic": "{topic}",
  "option_a": "33.33%",
  "option_b": "50%",
  "option_c": "66.67%",
  "option_d": "75%",
  "correct_answer": "B",
  "explanation": "Profit = 150 - 100 = 50. Profit % = (50/100) × 100 = 50%",
  "xp_reward": 10
}}]

Return ONLY valid JSON, no other text."""

    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """Validate question structure and content."""
        required_fields = [
            "title",
            "description",
            "category",
            "difficulty",
            "topic",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "explanation",
            "xp_reward",
        ]

        if not all(field in question for field in required_fields):
            return False

        if question.get("correct_answer", "").upper() not in ["A", "B", "C", "D"]:
            return False

        if question.get("category") not in ["Quants", "Logical", "Language"]:
            return False

        try:
            xp = int(question.get("xp_reward", 0))
            if xp < 5 or xp > 50:
                return False
        except (ValueError, TypeError):
            return False

        if len(str(question.get("title", ""))) < 5 or len(str(question.get("title", ""))) > 100:
            return False

        return True


def get_question_generator() -> QuestionGenerator:
    """Get singleton instance of QuestionGenerator."""
    return QuestionGenerator()

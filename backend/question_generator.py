"""
Question Generator - No-op stub (Groq/AI generation removed)

AI-based question generation has been removed.
Questions should be uploaded via the JSON bulk upload endpoint instead.
"""


class _DisabledGenerator:
    def generate_single(self, topic: str, difficulty: str, count: int = 1):
        return []


_instance = _DisabledGenerator()


def get_question_generator():
    """Returns a disabled generator stub."""
    return _instance

import random


_MOCK_REPLIES = {
    "happy": [
        "Hey. Good to hear from you.",
        "Hi. I'm here and ready when you are.",
    ],
    "focused": [
        "Got it. I'm listening. What else is on your mind?",
        "Noted. Keep going, I'm right here.",
        "Interesting. Tell me more when you're ready.",
        "I heard you. We'll figure this out together.",
        "On it. What's the next piece of the puzzle?",
        "That makes sense. Let's work through it step by step.",
        "I'm paying attention. What do you need from me right now?",
        "Understood. I'll keep that in mind going forward.",
    ],
    "neutral": [
        "You sent an empty message. Try saying something!",
    ],
}


def select_mock_mood(message: str) -> str:
    """
    Select a simple mock mood from the current message only.

    This does not call an LLM, read memory, or access the database.
    """
    normalized = message.strip().lower()
    if not normalized:
        return "neutral"
    if any(keyword in normalized.split() for keyword in ("hello", "hi")):
        return "happy"
    if "help" in normalized or "task" in normalized:
        return "focused"
    return "focused"


def format_mock_reply(message: str, mood: str) -> str:
    """
    Format a short mock reply for the selected mood.

    Message is accepted for the future service contract, but no persistence or
    external provider is used in mock mode.
    """
    if not message.strip():
        mood = "neutral"
    replies = _MOCK_REPLIES.get(mood, _MOCK_REPLIES["focused"])
    return random.choice(replies)

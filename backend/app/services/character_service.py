import random


_MOCK_REPLIES = {
    "casual": {
        "happy": [
            "Hey. Good to hear from you.",
            "Hi. I'm here and ready when you are.",
        ],
        "focused": [
            "Got it. I'm listening. What else is on your mind?",
            "Noted. Keep going, I'm right here.",
            "Interesting. Tell me more when you're ready.",
        ],
        "neutral": [
            "You sent an empty message. Try saying something!",
        ],
    },
    "project": {
        "happy": [
            "Good to see you. Let's pick the next concrete step.",
        ],
        "focused": [
            "Understood. Next step: clarify the goal, then choose the smallest useful action.",
            "Got it. Let's break this into one clear next task.",
        ],
        "neutral": [
            "Send the task or project note you want to work on.",
        ],
    },
    "debug": {
        "happy": [
            "Hi. Share the failing behavior and the latest error first.",
        ],
        "focused": [
            "Start with the exact error, reproduction steps, and the smallest failing case.",
            "Check the input, expected output, and the first point where behavior diverges.",
        ],
        "neutral": [
            "Send the error message or failing case to debug.",
        ],
    },
    "support": {
        "happy": [
            "Hey. I'm here with you. What's the main thing weighing on you?",
        ],
        "focused": [
            "I hear you. Let's name the problem clearly, then choose one manageable step.",
            "That sounds like a lot. Let's slow it down and handle one piece first.",
        ],
        "neutral": [
            "Tell me what's going on, even briefly.",
        ],
    },
    "reminder": {
        "happy": [
            "Hi. What should I help you keep track of?",
        ],
        "focused": [
            "Reminder noted in mock mode. Keep the next action short and specific.",
            "Set the reminder as one action, one time, and one expected outcome.",
        ],
        "neutral": [
            "Send what you want to be reminded about.",
        ],
    },
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


def format_mock_reply(message: str, mood: str, mode: str = "casual") -> str:
    """
    Format a short mock reply for the selected mood.

    Message is accepted for the future service contract, but no persistence or
    external provider is used in mock mode.
    """
    if not message.strip():
        mood = "neutral"
    mode_replies = _MOCK_REPLIES.get(mode, _MOCK_REPLIES["casual"])
    replies = mode_replies.get(mood, mode_replies["focused"])
    return random.choice(replies)

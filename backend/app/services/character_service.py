import random
import re


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
        "proud": [
            "Hmph. Of course I can handle that; watch closely.",
            "Naturally. I will show you how capable I am.",
        ],
        "annoyed": [
            "Hmph. Say it clearly, then I can decide what to do.",
            "Don't make this vague. Tell me the point directly.",
        ],
        "worried": [
            "Stay where you are. We will slow this down and check the risk first.",
            "That sounds unstable. Let's make it safe before moving.",
        ],
        "sleepy": [
            "If you are worn out, rest first. The task can wait a moment.",
            "You sound tired. Keep this small and do not push too hard.",
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


_WORD_PATTERN = re.compile(r"[a-z0-9']+")

_MOOD_KEYWORDS = {
    "sleepy": frozenset(
        {
            "asleep",
            "bed",
            "drowsy",
            "exhausted",
            "nap",
            "rest",
            "sleep",
            "sleepy",
            "tired",
            "weary",
        }
    ),
    "worried": frozenset(
        {
            "afraid",
            "anxious",
            "broken",
            "comfort",
            "concern",
            "concerned",
            "danger",
            "dangerous",
            "failed",
            "failure",
            "offline",
            "panic",
            "risk",
            "risky",
            "safe",
            "safety",
            "scared",
            "uncertain",
            "unsafe",
            "worried",
            "worry",
        }
    ),
    "annoyed": frozenset(
        {
            "angry",
            "annoyed",
            "annoying",
            "bother",
            "irritated",
            "irritating",
            "mad",
            "nag",
            "scold",
            "scolding",
            "tsundere-annoyed",
        }
    ),
    "proud": frozenset(
        {
            "boast",
            "boasting",
            "confident",
            "confidence",
            "glorious",
            "pride",
            "proud",
            "self-satisfied",
            "smug",
            "triumph",
            "triumphant",
            "victorious",
            "victory",
        }
    ),
    "happy": frozenset(
        {
            "cheer",
            "encourage",
            "encouragement",
            "excellent",
            "glad",
            "good",
            "great",
            "happy",
            "hello",
            "hi",
            "nice",
            "thanks",
            "yay",
        }
    ),
    "neutral": frozenset(
        {
            "factual",
            "neutral",
            "plain",
            "status",
            "summary",
        }
    ),
    "focused": frozenset(
        {
            "analyze",
            "bug",
            "code",
            "debug",
            "fix",
            "focus",
            "focused",
            "help",
            "implement",
            "plan",
            "project",
            "review",
            "task",
            "test",
            "work",
        }
    ),
}

_MOOD_PHRASES = {
    "sleepy": (
        "go to sleep",
        "need sleep",
        "need to sleep",
        "take a nap",
    ),
    "worried": (
        "not sure",
        "can't reach",
        "cannot reach",
        "feel safe",
        "is unsafe",
        "may fail",
        "might fail",
        "went offline",
    ),
    "annoyed": (
        "cut it out",
        "stop it",
        "tsundere scolding",
    ),
    "proud": (
        "praise me",
        "self satisfied",
        "self-satisfied",
        "show off",
        "tsundere pride",
    ),
    "happy": (
        "good job",
        "thank you",
        "thanks a lot",
    ),
    "neutral": (
        "just the facts",
        "neutral factual",
        "plain factual",
    ),
}


def _message_terms(message: str) -> tuple[str, set[str]]:
    normalized = message.strip().lower()
    return normalized, set(_WORD_PATTERN.findall(normalized))


def select_mock_mood(message: str) -> str:
    """
    Select a deterministic mock mood from the current message only.

    This does not call an LLM, read memory, or access the database.
    """
    normalized, words = _message_terms(message)
    if not normalized:
        return "neutral"

    for mood in (
        "worried",
        "sleepy",
        "annoyed",
        "proud",
        "happy",
        "neutral",
        "focused",
    ):
        if words.intersection(_MOOD_KEYWORDS[mood]):
            return mood
        if any(phrase in normalized for phrase in _MOOD_PHRASES.get(mood, ())):
            return mood

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
    replies = (
        mode_replies.get(mood)
        or _MOCK_REPLIES["casual"].get(mood)
        or mode_replies["focused"]
    )
    return random.choice(replies)

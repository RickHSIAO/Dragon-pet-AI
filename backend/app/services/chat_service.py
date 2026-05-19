from app.services.character_service import format_mock_reply, select_mock_mood


def generate_mock_chat_reply(message: str) -> dict[str, str]:
    """
    Generate a mock chat response without external AI, database, or memory.
    """
    mood = select_mock_mood(message)
    reply = format_mock_reply(message, mood)

    return {
        "reply": reply,
        "mood": mood,
        "source": "mock",
    }

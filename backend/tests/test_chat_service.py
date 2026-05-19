from app.services.chat_service import generate_mock_chat_reply


def test_empty_message_returns_fallback():
    response = generate_mock_chat_reply("   ")

    assert response == {
        "reply": "You sent an empty message. Try saying something!",
        "mood": "neutral",
        "source": "mock",
    }


def test_valid_message_returns_mock_source():
    response = generate_mock_chat_reply("Can you help me plan this?")

    assert response["reply"]
    assert response["mood"] == "focused"
    assert response["source"] == "mock"


def test_hello_returns_valid_mood_and_reply():
    response = generate_mock_chat_reply("hello")

    assert response["reply"]
    assert response["mood"] == "happy"
    assert response["source"] == "mock"

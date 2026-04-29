# tests/test_chat_engine.py
from unittest.mock import MagicMock, patch
from app.services.chat_engine import ChatEngine, DIVORCE_FIELDS


def make_engine():
    with patch("app.services.chat_engine.Groq"):
        return ChatEngine()


def test_divorce_fields_all_present():
    assert "author_name" in DIVORCE_FIELDS
    assert "author_cpf" in DIVORCE_FIELDS
    assert "defendant_name" in DIVORCE_FIELDS
    assert "marriage_date" in DIVORCE_FIELDS
    assert "marriage_regime" in DIVORCE_FIELDS
    assert "has_children" in DIVORCE_FIELDS
    assert "has_assets" in DIVORCE_FIELDS


def test_get_missing_fields_empty_data():
    engine = make_engine()
    missing = engine.get_missing_fields({})
    assert set(DIVORCE_FIELDS.keys()) == set(missing)


def test_get_missing_fields_partial_data():
    engine = make_engine()
    data = {"author_name": "Maria Silva", "author_cpf": "123.456.789-00"}
    missing = engine.get_missing_fields(data)
    assert "author_name" not in missing
    assert "author_cpf" not in missing
    assert "defendant_name" in missing


def test_is_collection_complete_false():
    engine = make_engine()
    assert engine.is_collection_complete({}) is False
    assert engine.is_collection_complete({"author_name": "Maria"}) is False


def test_is_collection_complete_true():
    engine = make_engine()
    complete_data = {field: "value" for field in DIVORCE_FIELDS}
    assert engine.is_collection_complete(complete_data) is True


def test_process_message_returns_string():
    with patch("app.services.chat_engine.Groq") as mock_groq:
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Olá! Vamos começar."))]
        )

        engine = ChatEngine()
        history = []
        collected_data = {}
        response, updated_data = engine.process_message(
            user_message="Olá",
            history=history,
            collected_data=collected_data,
        )

    assert isinstance(response, str)
    assert len(response) > 0
    assert isinstance(updated_data, dict)

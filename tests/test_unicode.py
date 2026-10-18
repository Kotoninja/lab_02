from src.streamstats.models import create_event


def test_unicode():
    e = create_event(
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "level": "INFO",
            "source": "проверка юникода в source",
            "message": "проверка юникода в сообщении",
        }
    )
    assert e.source == "проверка юникода в source"
    assert e.message == "проверка юникода в сообщении"

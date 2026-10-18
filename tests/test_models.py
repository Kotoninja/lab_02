import pytest

from src.streamstats import errors, models


def test_ok():
    e = models.create_event(
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "level": "INFO",
            "source": "test",
            "message": "helloworld",
        }
    )
    assert e.level == "INFO"
    assert e.source == "test"


def test_no_timestamp():
    with pytest.raises(errors.InvalidEventError) as e:
        models.create_event(
            {"level": "INFO", "source": "test", "message": "helloworld"}
        )
    assert "timestamp" in str(e.value)


def test_no_level():
    with pytest.raises(errors.InvalidEventError) as e:
        models.create_event(
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "source": "test",
                "message": "helloworld",
            }
        )
    assert "level" in str(e.value)


def test_no_source():
    with pytest.raises(errors.InvalidEventError) as e:
        models.create_event(
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "level": "INFO",
                "message": "helloworld",
            }
        )
    assert "source" in str(e.value)


def test_no_message():
    with pytest.raises(errors.InvalidEventError) as e:
        models.create_event(
            {"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "source": "test"}
        )
    assert "message" in str(e.value)


def test_bad_level():
    with pytest.raises(errors.InvalidEventError) as e:
        models.create_event(
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "level": "TRACE",
                "source": "test",
                "message": "helloworld",
            }
        )
    assert "TRACE" in str(e.value)


def test_invalid_timestamp():
    with pytest.raises(errors.InvalidTimestampError):
        models.create_event(
            {
                "timestamp": "нет",
                "level": "INFO",
                "source": "test",
                "message": "helloworld",
            }
        )


def test_timestamp_without_timezone():
    with pytest.raises(errors.InvalidTimestampError):
        models.create_event(
            {
                "timestamp": "2024-01-01T10:00:00",
                "level": "INFO",
                "source": "test",
                "message": "helloworld",
            }
        )


def test_invalid_message():
    with pytest.raises(errors.InvalidEventError):
        models.create_event(
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "level": "INFO",
                "source": "auth",
                "message": 123,
            }
        )

def test_invalid_source():
    with pytest.raises(errors.InvalidEventError):
        models.create_event(
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "level": "INFO",
                "source": "",
                "message": "text",
            }
        )
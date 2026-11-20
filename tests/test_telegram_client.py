import io

import pytest
import requests

from scripts.daily_telegram.telegram import TelegramClient


class FakeResponse:
    def __init__(self, status):
        self.status_code = status

    def json(self):
        return {"parameters": {"retry_after": 0}}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("scripts.daily_telegram.telegram.time.sleep", lambda _s: None)


def test_retry_resends_the_whole_file(monkeypatch):
    bodies = []
    statuses = iter([500, 200])

    def fake_post(url, data, files, timeout):
        bodies.append(files["photo"].read())
        return FakeResponse(next(statuses))

    monkeypatch.setattr("scripts.daily_telegram.telegram.requests.post", fake_post)
    TelegramClient("t", "c")._post("sendPhoto", {"chat_id": "c"}, files={"photo": io.BytesIO(b"image-bytes")})
    assert bodies == [b"image-bytes", b"image-bytes"]


def test_rate_limit_on_last_attempt_raises_instead_of_dropping_the_message(monkeypatch):
    monkeypatch.setattr(
        "scripts.daily_telegram.telegram.requests.post", lambda *a, **k: FakeResponse(429)
    )
    with pytest.raises(requests.HTTPError):
        TelegramClient("t", "c")._post("sendMessage", {"chat_id": "c", "text": "x"}, retries=2)

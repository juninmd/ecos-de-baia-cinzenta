import pytest

from scripts.daily_telegram import speech


def test_say_propaga_ctrl_c(monkeypatch, tmp_path):
    """KeyboardInterrupt durante a síntese não pode ser engolido como falha de TTS."""

    def interrompido(coro):
        coro.close()
        raise KeyboardInterrupt

    monkeypatch.setattr(speech.asyncio, "run", interrompido)
    with pytest.raises(KeyboardInterrupt):
        speech.say("olá", None, tmp_path / "fala.mp3")

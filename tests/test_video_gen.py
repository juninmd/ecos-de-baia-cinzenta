import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from scripts.video_gen.audio import generate_narration
from scripts.video_gen.composer import VideoComposer
from scripts.video_gen.main import VideoPipeline
from scripts.video_gen.parser import ChapterParser
from scripts.video_gen.wan_client import WanVideoGenerator


@pytest.fixture
def sample_chapter(tmp_path):
    chapter_file = tmp_path / "capitulo-1.md"
    content = "---\nimage: /capitulo_1.jpg\n---\n# Título do Capítulo\n\nEste é o texto do teste. Tem mais de 50 caracteres para garantir que o parse seja válido.\n"
    chapter_file.write_text(content, encoding='utf-8')
    return chapter_file


def test_chapter_parser(sample_chapter):
    result = ChapterParser.parse_chapter(sample_chapter)
    assert result['numero'] == '1'
    assert result['titulo'] == 'Título do Capítulo'
    assert 'texto do teste' in result['texto']


@patch('pydub.AudioSegment')
@patch('gtts.gTTS')
def test_audio_generation(mock_gtts, mock_audio, tmp_path):
    mock_gtts_instance = mock_gtts.return_value
    mock_audio_instance = mock_audio.from_file.return_value
    mock_audio_instance.__len__.return_value = 5000  # 5000 ms = 5s

    out_path = tmp_path / "test.mp3"
    duration = generate_narration("Teste", out_path)

    mock_gtts_instance.save.assert_called_once_with(str(out_path))
    assert duration == 5.0


@patch('requests.Session.post')
def test_wan_client_success(mock_post, tmp_path):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_video_data"
    mock_post.return_value = mock_response

    os.environ['HF_TOKEN'] = 'test-token'
    client = WanVideoGenerator(tmp_path)

    vid_path = tmp_path / "test_out.mp4"
    success = client._generate_single_video("Test chunk max 1000", vid_path)

    assert success is True
    assert vid_path.exists()
    assert vid_path.read_bytes() == b"fake_video_data"


@patch('requests.Session.post')
@patch('time.sleep', return_value=None)
def test_wan_client_retry_503(mock_sleep, mock_post, tmp_path):
    mock_error_response = MagicMock()
    mock_error_response.status_code = 503
    mock_error = requests.exceptions.HTTPError(response=mock_error_response)

    mock_success_response = MagicMock()
    mock_success_response.status_code = 200
    mock_success_response.content = b"fake_video_data_retry"

    mock_post.side_effect = [mock_error, mock_success_response]

    client = WanVideoGenerator(tmp_path)
    vid_path = tmp_path / "test_retry.mp4"
    success = client._generate_single_video("Test", vid_path)

    assert success is True
    assert mock_post.call_count == 2
    assert mock_sleep.called


@patch('subprocess.run')
def test_composer_combine(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=0)

    composer = VideoComposer(tmp_path)
    composer._create_title_overlay = MagicMock(return_value=tmp_path / "overlay.png")

    vid_path = tmp_path / "fake_vid.mp4"
    vid_path.touch()
    audio_path = tmp_path / "fake_audio.mp3"
    audio_path.touch()
    out_vid = tmp_path / "final.mp4"

    composer.combine_videos([vid_path], audio_path, out_vid, "Title", "1")

    assert mock_run.call_count == 2


@patch('subprocess.run')
def test_composer_create_video_from_image(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=0)

    composer = VideoComposer(tmp_path)
    composer._create_title_overlay = MagicMock(return_value=tmp_path / "overlay.png")

    img_path = tmp_path / "cover.jpg"
    img_path.touch()
    audio_path = tmp_path / "audio.mp3"
    audio_path.touch()
    out_vid = tmp_path / "cover_video.mp4"

    composer.create_video_from_image(img_path, audio_path, out_vid, "Title", "7")

    assert mock_run.call_count == 1
    cmd = mock_run.call_args.args[0]
    assert "-loop" in cmd
    assert str(img_path) in cmd


def test_pipeline_resolve_chapter_image(tmp_path):
    root = tmp_path
    (root / "docs" / "public").mkdir(parents=True)
    img = root / "docs" / "public" / "capitulo_1.jpg"
    img.touch()

    pipeline = VideoPipeline(root)
    found = pipeline._resolve_chapter_image("/capitulo_1.jpg")

    assert found == img

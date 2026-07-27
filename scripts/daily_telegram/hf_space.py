import os
import shutil
from pathlib import Path
from typing import Optional

KONTEXT_SPACE = "black-forest-labs/FLUX.1-Kontext-Dev"
LTX_SPACE = "Lightricks/ltx-video-distilled"
NEGATIVE_VIDEO = "worst quality, inconsistent motion, blurry, jittery, distorted face"

# ZeroGPU dá uma cota diária gratuita; quando ela acaba, insistir só queima tempo.
_exhausted = set()


def quota_exhausted(space: str) -> bool:
    return space in _exhausted


def _note_failure(space: str, exc: BaseException) -> None:
    if "quota" in str(exc).lower():
        _exhausted.add(space)
        print(f"🚫 Cota gratuita do ZeroGPU esgotada em {space}; usando fallback no resto do capítulo.")


def _client(space: str):
    from gradio_client import Client

    return Client(space, token=os.getenv("HF_TOKEN") or None, verbose=False)


def _extract_path(result) -> Optional[str]:
    """Gradio returns nested tuples/dicts; dig out the produced file path."""
    node = result
    while isinstance(node, (list, tuple)) and node:
        node = node[0]
    while isinstance(node, dict):
        node = node.get("video") or node.get("path") or node.get("url")
    return node if isinstance(node, str) else None


def edit_with_identity(
    reference: Path, prompt: str, output_path: Path, seed: int = 42, steps: int = 28
) -> Optional[Path]:
    """FLUX.1-Kontext: reframe a character portrait into a new scene, identity intact."""
    from gradio_client import handle_file

    if quota_exhausted(KONTEXT_SPACE):
        return None
    try:
        print(f"🧬 Kontext: mantendo identidade de {reference.name}...")
        result = _client(KONTEXT_SPACE).predict(
            input_image=handle_file(str(reference)),
            prompt=prompt,
            seed=seed,
            randomize_seed=False,
            guidance_scale=2.5,
            steps=steps,
            api_name="/infer",
        )
        origem = _extract_path(result)
        if not origem:
            raise ValueError("resposta sem imagem")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(origem, output_path)
        print(f"✅ Cena com identidade travada: {output_path.name}")
        return output_path
    except BaseException as exc:  # Space grátis: fila, quota ou app error
        print(f"⚠ Kontext indisponível ({type(exc).__name__}): {str(exc)[:120]}")
        _note_failure(KONTEXT_SPACE, exc)
        return None


def image_to_video(
    image: Path, motion_prompt: str, output_path: Path, duracao: int = 3, seed: int = 42
) -> Optional[Path]:
    """LTX-Video: animate a still into a real moving shot (free ZeroGPU queue)."""
    from gradio_client import handle_file

    if quota_exhausted(LTX_SPACE):
        return None
    try:
        print(f"🎞️ LTX: animando {image.name} ({duracao}s)...")
        result = _client(LTX_SPACE).predict(
            prompt=motion_prompt,
            negative_prompt=NEGATIVE_VIDEO,
            input_image_filepath=handle_file(str(image)),
            input_video_filepath=None,
            height_ui=512,
            width_ui=704,
            mode="image-to-video",
            duration_ui=duracao,
            ui_frames_to_use=9,
            seed_ui=seed,
            randomize_seed=False,
            ui_guidance_scale=1,
            improve_texture_flag=False,
            api_name="/image_to_video",
        )
        origem = _extract_path(result)
        if not origem:
            raise ValueError("resposta sem vídeo")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(origem, output_path)
        print(f"✅ Clipe animado: {output_path.name}")
        return output_path
    except BaseException as exc:
        print(f"⚠ LTX indisponível ({type(exc).__name__}): {str(exc)[:120]}")
        _note_failure(LTX_SPACE, exc)
        return None

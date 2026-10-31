"""Script auxiliar para garantir que todos os pesos do Qwen-Image-2.1 estejam em cache local."""
import sys
import time
from huggingface_hub import hf_hub_download

FILES = [
    "text_encoder/model-00001-of-00004.safetensors",
    "text_encoder/model-00002-of-00004.safetensors",
    "text_encoder/model-00003-of-00004.safetensors",
    "text_encoder/model-00004-of-00004.safetensors",
    "text_encoder/generation_config.json",
    "vae/diffusion_pytorch_model.safetensors",
]

def main():
    print("Iniciando verificação/download dos arquivos do Qwen-Image-2.1...")
    for f in FILES:
        t0 = time.time()
        print(f"Baixando/verificando {f}...", flush=True)
        path = hf_hub_download(repo_id="Qwen/Qwen-Image-2.1", filename=f)
        print(f"  OK em {time.time()-t0:.1f}s -> {path}", flush=True)
    print("Todos os pesos estão prontos no cache local!")

if __name__ == "__main__":
    main()

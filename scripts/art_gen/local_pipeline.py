import os

try:
    import torch
    from diffusers import FluxPipeline, StableDiffusionPipeline, StableDiffusionXLPipeline
except ImportError:
    torch = None
    FluxPipeline = None
    StableDiffusionPipeline = None
    StableDiffusionXLPipeline = None

from .config import MODEL_ALTERNATIVES

class LocalPipelineManager:
    """Manages the initialization and configuration of local Stable Diffusion pipelines."""

    def __init__(self, model_family):
        self.model_family = model_family
        self.device = "cpu"
        self.pipeline = None

    def setup_pipeline(self):
        if not (torch and StableDiffusionPipeline):
            print("⚠️ Diffusers/Torch not installed. Local generation unavailable.")
            return False

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.device == "cpu":
            print("⚠️ No GPU detected. Local generation will be slow.")

        model_cfg = MODEL_ALTERNATIVES.get(self.model_family)
        if not model_cfg:
            print(f"❌ Unknown model family '{self.model_family}'.")
            return False

        model_id = os.environ.get("ART_MODEL_ID", model_cfg["local_model_id"])
        print(f"⚙️ Initializing local pipeline '{self.model_family}' with {model_id} on {self.device}...")

        try:
            self._load_and_configure_pipeline(model_id)
            print(f"✅ Local pipeline ready with '{self.model_family}'.")
            return True
        except Exception as e:
            print(f"❌ Failed to load local model '{model_id}' ({self.model_family}): {e}")
            self.pipeline = None
            return False

    def _load_and_configure_pipeline(self, model_id):
        pipeline = self._load_pipeline(self.model_family, model_id)
        pipeline.to(self.device)

        if hasattr(pipeline, "enable_attention_slicing"):
            pipeline.enable_attention_slicing()

        self.pipeline = pipeline

    def _load_pipeline(self, family, model_id):
        if family == "flux-schnell":
            if FluxPipeline is None:
                raise RuntimeError("FluxPipeline is unavailable in the current version of diffusers.")
            dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
            return FluxPipeline.from_pretrained(model_id, torch_dtype=dtype)

        if family == "sdxl":
            if StableDiffusionXLPipeline is None:
                raise RuntimeError("StableDiffusionXLPipeline is unavailable in the current version of diffusers.")
            dtype = torch.float16 if self.device == "cuda" else torch.float32
            return StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)

        return StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)

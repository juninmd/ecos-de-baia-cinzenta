import os

from .config import MODEL_ALTERNATIVES


class ImageGenerator:
    def __init__(self, api_url=None, model_family="sdxl"):
        self.api_url = api_url or os.environ.get("SD_API_URL")
        self.allow_cpu_fallback = os.environ.get("ART_ALLOW_CPU_FALLBACK", "0").lower() in {
            "1", "true", "yes", "on"
        }
        self.remote_timeout = int(os.environ.get("SD_API_TIMEOUT", "120"))
        self.model_family = model_family
        self.negative_prompt = (
            "low quality, blurry, bad anatomy, extra limbs, deformed face, duplicated character, "
            "text, watermark, logo, frame, jpeg artifacts, cartoon, anime"
        )

        from .local_pipeline import LocalPipelineManager
        self.local_manager = LocalPipelineManager(model_family)
        self.session = None
        self._configure_api_url()

    def _get_session(self):
        if self.session is None:
            import requests
            self.session = requests.Session()
        return self.session

    def _configure_api_url(self):
        """Attempts to auto-detect a local SD API if no URL was explicitly provided."""
        if not self.api_url:
            default_url = "http://127.0.0.1:7860"
            if self._is_remote_available(default_url):
                self.api_url = default_url
                print(f"ℹ️ SD_API_URL not set. Using detected local API at {self.api_url}")

    def _is_remote_available(self, base_url):
        try:
            session = self._get_session()
            response = session.get(f"{base_url}/sdapi/v1/options", timeout=2)
            return response.ok
        except Exception:
            return False

    def _remote_payload(self, prompt):
        cfg = MODEL_ALTERNATIVES[self.model_family]
        width, height = cfg["size"]
        payload = {
            "prompt": prompt,
            "negative_prompt": self.negative_prompt,
            "steps": cfg["steps"],
            "cfg_scale": 7.0 if self.model_family == "flux-schnell" else 7.5,
            "width": width,
            "height": height,
            "sampler_name": cfg["sampler"],
        }
        if self.model_family == "flux-schnell":
            payload["scheduler"] = "Simple"
        return payload

    def generate(self, prompt, output_path, dry_run=False):
        if dry_run:
            print(f"🧪 [DRY RUN] Would generate using '{self.model_family}' for prompt: {prompt}")
            return True

        if self.api_url:
            if self._is_remote_available(self.api_url):
                return self._generate_remote(prompt, output_path)
            print(f"⚠️ SD API unavailable at {self.api_url}. Falling back to local backend.")

        if not self._can_use_local_generation():
            return False

        if self.local_manager.pipeline is None:
            self.local_manager.setup_pipeline()

        if self.local_manager.pipeline:
            return self._generate_local(prompt, output_path)

        print("❌ No image generation backend available (No API URL and No Local pipeline).")
        return False

    def _can_use_local_generation(self):
        """Validates if local generation is allowed given the hardware and configuration."""
        try:
            import torch
            has_gpu = torch.cuda.is_available()
        except ImportError:
            has_gpu = False

        if not self.allow_cpu_fallback and not has_gpu:
            print(
                "⚠️ SD_API_URL is not configured/reachable and GPU is unavailable. "
                "Skipping local CPU generation for performance. "
                "Set SD_API_URL or ART_ALLOW_CPU_FALLBACK=1 to force CPU generation."
            )
            return False

        return True

    def _generate_remote(self, prompt, output_path):
        import requests
        import base64

        print(f"🌐 Sending to Remote SD API: {self.api_url} (model_family={self.model_family})")
        payload = self._remote_payload(prompt)

        try:
            session = self._get_session()
            resp = session.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=self.remote_timeout,
            )
            resp.raise_for_status()
            image_b64 = resp.json()['images'][0]

            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_b64))

            print(f"✅ Image saved to {output_path}")
            return True

        except requests.exceptions.Timeout:
            print(f"❌ Remote SD API request timed out after {self.remote_timeout} seconds")
        except Exception as e:
            print(f"❌ Remote Generation Failed: {e}")

        return False

    def _generate_local(self, prompt, output_path):
        device = self.local_manager.device
        print(f"🖥️ Generating locally on {device} with {self.model_family}...")
        try:
            cfg = MODEL_ALTERNATIVES[self.model_family]
            width, height = cfg["size"]

            if self.model_family == "flux-schnell":
                result = self.local_manager.pipeline(
                    prompt,
                    guidance_scale=3.5,
                    num_inference_steps=cfg["steps"],
                    width=width,
                    height=height,
                    max_sequence_length=512,
                )
            else:
                result = self.local_manager.pipeline(
                    prompt,
                    negative_prompt=self.negative_prompt,
                    num_inference_steps=cfg["steps"],
                    guidance_scale=7.5,
                    width=width,
                    height=height,
                )

            image = result.images[0]
            image.save(output_path)
            print(f"✅ Image saved to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Local Generation Failed: {e}")
            return False

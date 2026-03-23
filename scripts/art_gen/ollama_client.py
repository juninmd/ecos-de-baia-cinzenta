import os
import time


class OllamaClient:
    def __init__(self, host=None, model="llama3.1:8b"):
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = model
        self.api_url = f"{self.host}/api/generate"
        print(f"🦙 Initializing Ollama Client ({self.host}) with model: {self.model}...")

    def check_connection(self, max_retries=3, retry_delay=2):
        """
        Checks if the Ollama service is reachable.
        Includes retry logic to account for slow container startup times in CI environments.
        """
        import requests
        for attempt in range(max_retries):
            try:
                response = requests.get(self.host, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Successfully connected to Ollama at {self.host}")
                    return True
                raise requests.RequestException(f"HTTP {response.status_code}")
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Failed to connect to Ollama after {max_retries} attempts: {e}")
        return False

    def generate_prompt(self, chapter_text, active_characters, style):
        import requests

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(chapter_text, active_characters, style)

        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False
        }

        try:
            print("... Sending request to Ollama...")
            # We use a long timeout because text generation can take several minutes on CPU
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.Timeout:
            print("⚠️ Ollama request timed out after 300 seconds")
            return None
        except requests.RequestException as e:
            print(f"⚠️ Ollama Generation Failed: {e}")
            return None

    def _build_system_prompt(self):
        return (
            "You are a senior cinematic art director building prompts for a noir cyberpunk bestseller. "
            "Return ONE production-ready image prompt with coherent character continuity and strong storytelling."
        )

    def _build_user_prompt(self, chapter_text, active_characters, style):
        char_descriptions = [f"- {c['name']}: {c['description'][:240]}" for c in active_characters[:3]]
        char_context = "\n".join(char_descriptions) if char_descriptions else "- No named characters detected"

        return (
            "Select the single most dramatic visual moment from this chapter excerpt.\n"
            f"TARGET STYLE: {style}\n"
            "PRIORITY: preserve canonical character appearance and emotional tone.\n"
            f"CHARACTER BIBLE (must respect):\n{char_context}\n\n"
            f"CHAPTER TEXT:\n{chapter_text[:2400]}...\n\n"
            "INSTRUCTIONS:\n"
            "1. Write in English.\n"
            "2. Include framing and camera language (wide shot / close-up / lens feeling).\n"
            "3. Include lighting design, weather, texture, and atmosphere.\n"
            "4. Include exact character poses, action beat, and key props from scene.\n"
            "5. Keep continuity with canon visuals and avoid generic substitutions.\n"
            "6. Output only the final prompt text, no quotes, no explanations.\n"
            "7. Max 170 words.\n"
            "8. End with: ultra cinematic, noir cyberpunk, volumetric rain, film grain, masterpiece."
        )

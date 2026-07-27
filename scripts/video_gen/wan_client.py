import os
import re
import time
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed


class WanVideoGenerator:
    """Generates video using Wan-AI/Wan2.2-TI2V-5B on Hugging Face."""
    
    API_URL = "https://api-inference.huggingface.co/models/Wan-AI/Wan2.2-TI2V-5B"
    
    def __init__(self, output_dir: Path):
        self.api_key = os.environ.get('HF_TOKEN')
        self.output_dir = output_dir
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        self.session = None
        
        if not self.api_key:
            print("⚠️ HF_TOKEN environment variable not set. Assuming Space API or local URL is configured, or API will fail.")

    def _get_session(self):
        if self.session is None:
            import requests
            self.session = requests.Session()
            self.session.headers.update(self.headers)
        return self.session

    def _query(self, payload):
        session = self._get_session()
        response = session.post(self.API_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.content

    def _generate_single_video(self, chunk: str, output_path: Path) -> bool:
        import requests
        """
        Calls the Wan2.2 API with a cinematic prompt.
        Because video generation on HF API might require polling, we try an initial request.
        """
        prompt = (
            "Cinematic Cyberpunk Noir digital art video. Cinematic atmospheric lighting, "
            "high contrast, teal and orange neon, rainy night in Baía Cinzenta. "
            "Intricate details, 8k resolution, photorealistic style. "
            f"Scene detail: {chunk[:1000]}"
        )
        
        print(f"  🎬 Prompting Wan2.2-TI2V-5B: {prompt[:60]}...")
        
        try:
            video_bytes = self._query({"inputs": prompt})
            
            # If the API returns JSON with an 'error' (like Model is loading...)
            # we should normally handle it, but requests will raise status code error 
            # for 503 model loading. Wait, HF sometimes returns 503 for loading.
            
            with open(output_path, "wb") as f:
                f.write(video_bytes)
                
            print(f"  ✓ Success: Video saved to {output_path.name}")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                # Model is loading
                print("  ⏳ Model is loading. Retrying in 20 seconds...")
                time.sleep(20)
                try:
                    video_bytes = self._query({"inputs": prompt})
                    with open(output_path, "wb") as f:
                        f.write(video_bytes)
                    print(f"  ✓ Success: Video saved to {output_path.name}")
                    return True
                except Exception as inner_e:
                    print(f"  ❌ Retry failed: {inner_e}")            
            print(f"  ❌ API Error: {e.response.text if hasattr(e.response, 'text') else e}")
            return False
            
        except Exception as e:
            print(f"  ❌ Connection/Timeout Error: {e}")
            return False

    def generate_multi_scene_videos(self, chapter_num: str, texto: str) -> List[Path]:
        """Split chapter text into 8 segments and generate a video for each."""
        print(f"🤖 Generating 8 dynamic video scenes for Chapter {chapter_num} via Wan2.2...")
        
        # Split text into 8 roughly equal parts
        paragraphs = [p for p in texto.split('\n') if len(p.strip()) > 50]
        if len(paragraphs) < 8:
            sentences = re.split(r'(?<=[.!?])\s+', texto)
            if len(sentences) < 8:
                chunk_size = len(texto) // 8
                chunks = [texto[i:i+chunk_size] for i in range(0, len(texto), chunk_size)][:8]
            else:
                step = len(sentences) // 8
                chunks = [' '.join(sentences[i:i+step]) for i in range(0, len(sentences), step)][:8]
        else:
            step = len(paragraphs) // 8
            chunks = [' '.join(paragraphs[i:i+step]) for i in range(0, len(paragraphs), step)][:8]
            
        video_paths = []

        def process_scene(i, chunk):
            vid_path = self.output_dir / f"capitulo_{chapter_num}_scene_{i}.mp4"
            
            if vid_path.exists() and vid_path.stat().st_size > 10000:
                print(f"  ⏭ Using cached video for scene {i}")
                return i, vid_path, True
                
            print(f"  🎬 Generating scene {i}/8...")
            success = self._generate_single_video(chunk, vid_path)
            return i, vid_path, success

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = executor.map(lambda t: process_scene(*t), enumerate(chunks, 1))

        for i, vid_path, success in results:
            if success and vid_path.exists() and vid_path.stat().st_size > 5000:
                video_paths.append(vid_path)
            else:
                print(f"  ⚠️ Scene {i} failed. Using fallback if available.")
                
        return video_paths

#!/usr/bin/env python3
"""
Video Generator for "Ecos de Baía Cinzenta"
Generates cinematic noir videos from book chapters using open-source tools.

Dependencies:
- Kokoro TTS: Natural Portuguese narration
- Movis: Video composition and effects
- Pydub: Audio processing
"""

import argparse
import re
import sys
import os
import io
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


class ChapterParser:
    """Extracts metadata and content from markdown chapters."""
    
    @staticmethod
    def parse_chapter(chapter_path: Path) -> Dict[str, str]:
        """
        Parse chapter markdown file.
        
        Args:
            chapter_path: Path to capitulo-*.md file
            
        Returns:
            Dict with: numero, titulo, texto, image_path
        """
        if not chapter_path.exists():
            raise FileNotFoundError(f"Chapter not found: {chapter_path}")
        
        content = chapter_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Extract frontmatter
        image_path = None
        if lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    break
                if line.startswith('image:'):
                    image_path = line.split(':', 1)[1].strip()
        
        # Extract title (first # heading)
        titulo = "Capítulo"
        for line in lines:
            if line.startswith('# '):
                titulo = line[2:].strip()
                break
        
        # Extract chapter number from filename
        numero = re.search(r'capitulo-(\d+)', chapter_path.name)
        numero = numero.group(1) if numero else "0"
        
        # Extract text (skip frontmatter and title)
        texto_lines = []
        skip_frontmatter = False
        skip_title = False
        
        for line in lines:
            if line.strip() == '---':
                skip_frontmatter = not skip_frontmatter
                continue
            if skip_frontmatter:
                continue
            if line.startswith('# ') and not skip_title:
                skip_title = True
                continue
            if line.strip():
                texto_lines.append(line)
        
        texto = '\n'.join(texto_lines).strip()
        
        return {
            'numero': numero,
            'titulo': titulo,
            'texto': texto,
            'image_path': image_path,
            'path': str(chapter_path)
        }


class VideoGenerator:
    """Generates cinematic videos with TTS narration and noir effects."""
    
    def __init__(self, project_root: Path, output_dir: Optional[Path] = None):
        """
        Initialize video generator.
        
        Args:
            project_root: Root directory of the project
            output_dir: Output directory for videos (default: docs/public/videos)
        """
        self.root = project_root
        self.output_dir = output_dir or (project_root / 'docs' / 'public' / 'videos')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = project_root / '.temp_video'
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_narration(self, texto: str, output_path: Path) -> float:
        """
        Generate TTS narration using gTTS (stable choice).
        
        Args:
            texto: Text to narrate
            output_path: Output audio file path
            
        Returns:
            Duration in seconds
        """
        from gtts import gTTS
        from pydub import AudioSegment
        
        # Limit text to avoid extremely long videos
        max_chars = 3000
        if len(texto) > max_chars:
            print(f"⚠ Text truncated from {len(texto)} to {max_chars} chars")
            texto = texto[:max_chars] + "..."
        
        print(f"🎙 Generating narration (Normal PT-BR)...")
        
        # Using pt-BR for better flow. No pitch shifting to avoid 'ET' effect.
        tts = gTTS(text=texto, lang='pt', tld='com.br', slow=False)
        tts.save(str(output_path))
        
        # Get audio duration
        audio = AudioSegment.from_file(str(output_path))
        duration = len(audio) / 1000.0  # Convert to seconds
        
        print(f"✓ Narration created: {duration:.1f}s")
        return duration

    def _generate_multi_scene_images(self, chapter_num: str, texto: str) -> List[Path]:
        """Split chapter text into 8 segments and generate an image for each."""
        print(f"🍌 Generating 8 dynamic scenes for Chapter {chapter_num}...")
        
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
            
        image_paths = []
        for i, chunk in enumerate(chunks, 1):
            img_path = self.root / 'docs' / 'public' / f"capitulo_{chapter_num}_scene_{i}.jpg"
            
            # For testing, we can check if it's already there and not just a black placeholder
            if img_path.exists() and img_path.stat().st_size > 5000:
                image_paths.append(img_path)
                continue
                
            print(f"  🎬 Generating scene {i}/8...")
            try:
                # Optimized: Call generation directly in-process
                success = self._generate_single_scene(chunk, img_path)
                
                if not success:
                    print(f"  ❌ Scene {i} generation returned False")
                
                if img_path.exists() and img_path.stat().st_size > 5000:
                    image_paths.append(img_path)
                else:
                    print(f"  ⚠️ Scene {i} produced invalid/placeholder image.")
                    main_img = self.root / 'docs' / 'public' / f"capitulo_{chapter_num}.jpg"
                    if main_img.exists():
                        image_paths.append(main_img)
            except Exception as e:
                print(f"  ⚠️ Scene {i} execution error: {e}")
        
        return image_paths

    def _generate_single_scene(self, chunk: str, output_path: Path) -> bool:
        """
        Generate a single image using NanoBanana (Google GenAI) directly.
        Includes fallback generation on failure.
        """
        try:
            from google import genai
            from PIL import Image
        except ImportError as e:
            print(f"Error importing dependencies: {e}")
            return self._generate_fallback(output_path)

        # Try all possible key names from the project
        api_key = (
            os.environ.get('NANO_BANANA_API_KEY_IMAGE') or
            os.environ.get('NANO_BANANA_API_KEY') or
            os.environ.get('GOOGLE_API_KEY')
        )

        if not api_key:
            print("Error: No API key found in environment.")
            return self._generate_fallback(output_path)

        client = genai.Client(api_key=api_key)
        
        # Richer narrative prompt
        prompt = (
            "Cinematic Cyberpunk Noir digital art. Cinematic atmospheric lighting, "
            "high contrast, teal and orange neon, rainy night in Baía Cinzenta. "
            "Intricate details, 8k resolution, photorealistic style. "
            f"Scene detail: {chunk[:1000]}"
        )

        try:
            # Use a more standard model name for 2026 SDK if flash-image fails
            model_name = 'imagen-3.0-generate-001' # Standard for high quality image gen

            response = client.models.generate_content(
                model=model_name,
                contents=[prompt]
            )

            if response.parts:
                for part in response.parts:
                    if part.inline_data:
                        img = Image.open(io.BytesIO(part.inline_data.data))
                        img.save(str(output_path))
                        print("Success: Image saved.")
                        return True
            print("Error: No image parts in response.")
            return self._generate_fallback(output_path)
        except Exception as e:
            print(f"Generation Exception: {e}")
            return self._generate_fallback(output_path)

    def _generate_fallback(self, output_path: Path) -> bool:
        """Create a fallback placeholder image."""
        try:
            from PIL import Image
            img = Image.new('RGB', (1920, 1080), color=(20, 20, 40))
            img.save(str(output_path))
            return False
        except Exception as e:
            print(f"Fallback generation failed: {e}")
            return False

    def create_video(self, capitulo: Dict[str, str]) -> Path:
        """
        Create complete video with effects.
        
        Args:
            capitulo: Chapter data dict
            
        Returns:
            Path to generated video
        """
        numero = capitulo['numero']
        titulo = capitulo['titulo']
        texto = capitulo['texto']
        
        print(f"\n{'='*60}")
        print(f"🎬 Processing Capítulo {numero}: {titulo}")
        print(f"{'='*60}")
        
        # Image Generation: Generate 8 images per chapter
        image_paths = self._generate_multi_scene_images(numero, texto)
        if not image_paths:
            print("⚠️ No images generated. Creating minimal backup...")
            # Create a backup image if all failed
            backup_path = self.root / 'docs' / 'public' / f"capitulo_{numero}.jpg"
            if not backup_path.exists():
                from PIL import Image
                img = Image.new('RGB', (1920, 1080), color=(10, 15, 25))
                img.save(backup_path)
            image_paths = [backup_path]
        
        # File paths
        output_video = self.output_dir / f"capitulo_{numero}.mp4"
        audio_path = self.temp_dir / f"cap_{numero}_narration.mp3"
        
        # Generate narration
        duration = self.generate_narration(texto, audio_path)
        
        # Ensure minimum duration
        video_duration = max(duration, 10.0)
        
        # Create animated video
        print("🎨 Creating expanded video composition (8 scenes)...")
        self._create_simple_video(
            output_path=output_video,
            audio_path=audio_path,
            titulo=titulo,
            numero=numero,
            duration=video_duration,
            image_paths=image_paths
        )
        
        print(f"✅ Video created: {output_video}")
        return output_video
    
    def _create_simple_video(
        self, 
        output_path: Path, 
        audio_path: Path,
        titulo: str,
        numero: str,
        duration: float,
        image_paths: List[Path]
    ):
        """
        Create animated video with dynamic effects.
        """
        from animated_composer import AnimatedVideoComposer
        
        # Create animated sequence
        composer = AnimatedVideoComposer(self.temp_dir)
        composer.create_animated_sequence(
            image_paths=image_paths,
            duration=duration,
            titulo=titulo,
            numero=numero,
            output_path=output_path,
            audio_path=audio_path
        )
    
    def cleanup(self):
        """Remove temporary files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("🧹 Temporary files cleaned")


def main():
    parser = argparse.ArgumentParser(description='Generate videos for book chapters')
    parser.add_argument(
        '--chapter', '-c',
        type=int,
        help='Chapter number (e.g., 1 for capitulo-1.md)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all chapters'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output directory (default: docs/public/videos)'
    )
    
    args = parser.parse_args()
    
    # Project root
    root = Path(__file__).parent.parent
    docs_dir = root / 'docs'
    
    # Initialize generator
    generator = VideoGenerator(root, args.output)
    
    try:
        if args.all:
            # Process all chapters
            chapters = sorted(docs_dir.glob('capitulo-*.md'))
            print(f"Found {len(chapters)} chapters")
            
            for cap_path in chapters:
                try:
                    capitulo = ChapterParser.parse_chapter(cap_path)
                    generator.create_video(capitulo)
                except Exception as e:
                    print(f"✗ Failed to process {cap_path.name}: {e}")
                    continue
        
        elif args.chapter:
            # Process single chapter
            cap_path = docs_dir / f'capitulo-{args.chapter}.md'
            capitulo = ChapterParser.parse_chapter(cap_path)
            generator.create_video(capitulo)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    finally:
        generator.cleanup()
    
    print("\n✨ Video generation complete!")


if __name__ == '__main__':
    main()

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
from pathlib import Path
from typing import Dict, Optional

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
        Generate TTS narration using gTTS.
        
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
        
        print(f"🎙 Generating narration ({len(texto)} chars)...")
        
        # Generate TTS
        tts = gTTS(text=texto, lang='pt', slow=False)
        tts.save(str(output_path))
        
        # Get audio duration
        audio = AudioSegment.from_file(str(output_path))
        duration = len(audio) / 1000.0  # Convert to seconds
        
        print(f"✓ Narration created: {duration:.1f}s")
        return duration
    
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
        print(f"🎬 Generating video for Capítulo {numero}: {titulo}")
        print(f"{'='*60}")
        
        # File paths
        output_video = self.output_dir / f"capitulo_{numero}.mp4"
        audio_path = self.temp_dir / f"cap_{numero}_narration.mp3"
        
        # Generate narration
        duration = self.generate_narration(texto, audio_path)
        
        # Ensure minimum duration
        video_duration = max(duration, 10.0)
        
        # Create video with simple composition (Movis alternative using moviepy)
        print("🎨 Creating video composition...")
        self._create_simple_video(
            output_path=output_video,
            audio_path=audio_path,
            titulo=titulo,
            numero=numero,
            duration=video_duration,
            image_path=capitulo.get('image_path')
        )
        
        print(f"✅ Video created: {output_video}")
        print(f"   Size: {output_video.stat().st_size / (1024*1024):.1f} MB")
        print(f"   Duration: {video_duration:.1f}s\n")
        
        return output_video
    
    def _create_simple_video(
        self, 
        output_path: Path, 
        audio_path: Path,
        titulo: str,
        numero: str,
        duration: float,
        image_path: Optional[str] = None
    ):
        """
        Create video using MoviePy (simpler than Movis for CI/CD).
        
        Falls back to static image + audio if complex effects fail.
        """
        try:
            from moviepy.editor import (
                AudioFileClip, 
                ImageClip, 
                TextClip, 
                CompositeVideoClip,
                ColorClip
            )
        except ImportError:
            print("⚠ MoviePy not available, creating minimal video")
            self._create_minimal_video(output_path, audio_path, duration)
            return
        
        # Load audio
        audio = AudioFileClip(str(audio_path))
        
        # Background
        if image_path and (self.root / 'docs' / 'public' / image_path.lstrip('/')).exists():
            bg_path = self.root / 'docs' / 'public' / image_path.lstrip('/')
            bg = ImageClip(str(bg_path)).set_duration(duration)
        else:
            # Dark background (noir aesthetic)
            bg = ColorClip(size=(1920, 1080), color=(10, 15, 25)).set_duration(duration)
        
        # Title overlay
        try:
            title_text = TextClip(
                f"CAPÍTULO {numero}\n{titulo}",
                fontsize=70,
                color='cyan',
                font='Arial-Bold',
                size=(1600, None),
                method='caption'
            ).set_position(('center', 100)).set_duration(5).crossfadein(1).crossfadeout(1)
            
            video = CompositeVideoClip([bg, title_text])
        except Exception as e:
            print(f"⚠ Title overlay failed: {e}, using simple bg")
            video = bg
        
        # Add audio and export
        video = video.set_audio(audio)
        video.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=2,
            logger=None  # Suppress verbose output
        )
        
        # Cleanup
        audio.close()
        video.close()
    
    def _create_minimal_video(self, output_path: Path, audio_path: Path, duration: float):
        """Ultra-minimal fallback: just combine image + audio with ffmpeg."""
        import subprocess
        
        # Create black frame
        black_image = self.temp_dir / 'black.png'
        from PIL import Image
        img = Image.new('RGB', (1920, 1080), color=(10, 15, 25))
        img.save(black_image)
        
        # Use ffmpeg
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', str(black_image),
            '-i', str(audio_path),
            '-c:v', 'libx264', '-tune', 'stillimage',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            '-t', str(duration),
            str(output_path)
        ]
        
        subprocess.run(cmd, capture_output=True)
    
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

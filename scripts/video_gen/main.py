import argparse
import sys
import shutil
from pathlib import Path

from scripts.video_gen.parser import ChapterParser
from scripts.video_gen.audio import generate_narration
from scripts.video_gen.wan_client import WanVideoGenerator
from scripts.video_gen.composer import VideoComposer


class VideoPipeline:
    def __init__(self, project_root: Path, output_dir: Path = None):
        self.root = project_root
        self.output_dir = output_dir or (project_root / 'docs' / 'public' / 'videos')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = project_root / '.temp_video'
        self.temp_dir.mkdir(exist_ok=True)
        
        self.generator = WanVideoGenerator(self.temp_dir)
        self.composer = VideoComposer(self.temp_dir)

    def cleanup(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("🧹 Temporary files cleaned")

    def process_chapter(self, chapter_path: Path):
        capitulo = ChapterParser.parse_chapter(chapter_path)
        numero = capitulo['numero']
        titulo = capitulo['titulo']
        texto = capitulo['texto']
        
        print(f"\n{'='*60}")
        print(f"🎬 Processing Capítulo {numero}: {titulo}")
        print(f"{'='*60}")
        
        # 1. Generate Video Clips (Text to Video) via Wan2.2
        video_paths = self.generator.generate_multi_scene_videos(numero, texto)
        if not video_paths:
            print("❌ Failed to generate any video clips.")
            return

        # 2. Generate Audio
        audio_path = self.temp_dir / f"cap_{numero}_narration.mp3"
        generate_narration(texto, audio_path)
        
        # 3. Combine with Audio & Overlays
        output_video = self.output_dir / f"capitulo_{numero}.mp4"
        self.composer.combine_videos(
            video_paths=video_paths,
            audio_path=audio_path,
            output_path=output_video,
            titulo=titulo,
            numero=numero
        )


def main():
    parser = argparse.ArgumentParser(description='Generate videos with Wan2.2-TI2V-5B')
    parser.add_argument('--chapter', '-c', type=int, help='Chapter number')
    parser.add_argument('--all', action='store_true', help='Process all chapters')
    parser.add_argument('--output', '-o', type=Path, help='Output directory')
    args = parser.parse_args()
    
    root = Path(__file__).resolve().parent.parent.parent
    docs_dir = root / 'docs'
    pipeline = VideoPipeline(root, args.output)
    
    try:
        if args.all:
            for cap_path in sorted(docs_dir.glob('capitulo-*.md')):
                try:
                    pipeline.process_chapter(cap_path)
                except Exception as e:
                    print(f"✗ Failed {cap_path.name}: {e}")
        elif args.chapter:
            cap_path = docs_dir / f'capitulo-{args.chapter}.md'
            pipeline.process_chapter(cap_path)
        else:
            parser.print_help()
            sys.exit(1)
    finally:
        pipeline.cleanup()
        print("\n✨ Video generation complete!")


if __name__ == '__main__':
    main()

import argparse
import sys
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Add root project dir to pythonpath to allow relative imports from scripts
root_dir = Path(__file__).absolute().parent.parent.parent
sys.path.insert(0, str(root_dir))

from scripts.video_gen.parser import ChapterParser
from scripts.video_gen.audio import generate_narration


class VideoPipeline:
    def __init__(self, project_root: Path, output_dir: Path = None):
        self.root = project_root
        self.output_dir = output_dir or (project_root / 'docs' / 'public' / 'videos')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = project_root / '.temp_video'
        self.temp_dir.mkdir(exist_ok=True)
        
        self.generator = None
        self.composer = None

    def cleanup(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("🧹 Temporary files cleaned")

    def _resolve_chapter_image(self, image_path: str) -> Path | None:
        if not image_path:
            return None

        normalized = image_path[1:] if image_path.startswith('/') else image_path
        candidate = self.root / 'docs' / 'public' / normalized
        if candidate.exists():
            return candidate

        direct = self.root / normalized
        if direct.exists():
            return direct
        return None

    def process_chapter(self, chapter_path: Path, mode: str = 'auto'):
        capitulo = ChapterParser.parse_chapter(chapter_path)
        numero = capitulo['numero']
        titulo = capitulo['titulo']
        texto = capitulo['texto']
        image_path = capitulo.get('image_path')
        
        print(f"\n{'='*60}")
        print(f"🎬 Processing Capítulo {numero}: {titulo}")
        print(f"{'='*60}")
        
        # 1. Generate Audio (shared by all modes)
        audio_path = self.temp_dir / f"cap_{numero}_narration.mp3"
        generate_narration(texto, audio_path)

        # 2. Generate visual track
        output_video = self.output_dir / f"capitulo_{numero}.mp4"
        source_image = self._resolve_chapter_image(image_path)
        use_image_mode = mode == 'image2video' or (mode == 'auto' and source_image is not None)

        if use_image_mode:
            if source_image is None:
                print("❌ No chapter image found for image2video mode.")
                return
            if self.composer is None:
                from scripts.video_gen.composer import VideoComposer
                self.composer = VideoComposer(self.temp_dir)
            self.composer.create_video_from_image(
                image_path=source_image,
                audio_path=audio_path,
                output_path=output_video,
                titulo=titulo,
                numero=numero,
            )
            return

        # fallback: text-to-video with Wan
        if self.generator is None:
            from scripts.video_gen.wan_client import WanVideoGenerator
            self.generator = WanVideoGenerator(self.temp_dir)
        video_paths = self.generator.generate_multi_scene_videos(numero, texto)
        if not video_paths:
            print("❌ Failed to generate any video clips.")
            return

        if self.composer is None:
            from scripts.video_gen.composer import VideoComposer
            self.composer = VideoComposer(self.temp_dir)
        self.composer.combine_videos(video_paths, audio_path, output_video, titulo, numero)


def main():
    parser = argparse.ArgumentParser(description='Generate chapter videos (text2video or image2video)')
    parser.add_argument('--chapter', '-c', type=int, help='Chapter number')
    parser.add_argument('--all', action='store_true', help='Process all chapters')
    parser.add_argument('--output', '-o', type=Path, help='Output directory')
    parser.add_argument(
        '--mode',
        choices=['auto', 'text2video', 'image2video'],
        default='auto',
        help='auto: uses chapter cover image when available, otherwise text2video',
    )
    args = parser.parse_args()
    
    root = Path(__file__).absolute().parent.parent.parent
    docs_dir = root / 'docs'
    pipeline = VideoPipeline(root, args.output)
    
    try:
        if args.all:
            futures_to_path = {}
            with ThreadPoolExecutor(max_workers=4) as executor:
                for cap_path in sorted(docs_dir.glob('capitulo-*.md')):
                    future = executor.submit(pipeline.process_chapter, cap_path, mode=args.mode)
                    futures_to_path[future] = cap_path

                for future in as_completed(futures_to_path):
                    cap_path = futures_to_path[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"✗ Failed {cap_path.name}: {e}")
        elif args.chapter:
            cap_path = docs_dir / f'capitulo-{args.chapter}.md'
            pipeline.process_chapter(cap_path, mode=args.mode)
        else:
            parser.print_help()
            sys.exit(1)
    finally:
        pipeline.cleanup()
        print("\n✨ Video generation complete!")


if __name__ == '__main__':
    main()

import subprocess
from pathlib import Path
from typing import List
from PIL import Image, ImageDraw, ImageFont


class VideoComposer:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(exist_ok=True)
        
        try:
            self.font_title = ImageFont.truetype("arial.ttf", 80)
            self.font_subtitle = ImageFont.truetype("arial.ttf", 50)
        except:
            self.font_title = ImageFont.load_default()
            self.font_subtitle = ImageFont.load_default()

    def _create_title_overlay(self, titulo: str, numero: str) -> Path:
        img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        title_text = f"CAPÍTULO {numero}"
        subtitle_text = titulo
        
        title_bbox = draw.textbbox((0, 0), title_text, font=self.font_title)
        title_w = title_bbox[2] - title_bbox[0]
        x_title = (1920 - title_w) // 2
        y_title = 100
        
        glow_color = (0, 255, 255, 85)
        for offset in [4, 3, 2, 1]:
            draw.text((x_title + offset, y_title + offset), title_text, font=self.font_title, fill=glow_color)
            
        draw.text((x_title, y_title), title_text, font=self.font_title, fill=(0, 255, 255, 255))
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=self.font_subtitle)
        subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
        x_subtitle = (1920 - subtitle_w) // 2
        
        draw.text((x_subtitle, y_title + 100), subtitle_text, font=self.font_subtitle, fill=(255, 255, 255, 255))
        
        overlay_path = self.temp_dir / "title_overlay.png"
        img.save(overlay_path)
        return overlay_path

    def combine_videos(self, video_paths: List[Path], audio_path: Path, output_path: Path, titulo: str, numero: str):
        print(f"🎬 Composing final video with {len(video_paths)} clips...")
        
        if not video_paths:
            print("⚠️ No video clips to combine.")
            return

        concat_file = self.temp_dir / "concat.txt"
        with open(concat_file, "w", encoding="utf-8") as f:
            for p in video_paths:
                f.write(f"file '{p.absolute().as_posix()}'\n")

        combined_video = self.temp_dir / "combined_no_audio.mp4"
        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
            "-i", str(concat_file), "-c", "copy", str(combined_video)
        ]
        res = subprocess.run(cmd_concat, capture_output=True)
        if res.returncode != 0:
            print("❌ ffmpeg concat failed. Falling back to first clip.")
            combined_video = video_paths[0]
            
        overlay_img = self._create_title_overlay(titulo, numero)
        
        print("🎬 Applying audio and effects (via ffmpeg loop)...")
        # -stream_loop -1 loops the video infinitely, -shortest cuts it when audio ends.
        cmd_final = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", str(combined_video),
            "-i", str(audio_path),
            "-i", str(overlay_img),
            "-filter_complex", 
            "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[bg];"
            "[bg][2:v]overlay=enable='between(t,0,5)'[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest", 
            str(output_path)
        ]
        
        result = subprocess.run(cmd_final, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ ffmpeg final encode failed: {result.stderr}")
        else:
            print(f"✅ Final video created: {output_path}")

    def create_video_from_image(
        self,
        image_path: Path,
        audio_path: Path,
        output_path: Path,
        titulo: str,
        numero: str,
        duration_seconds: int = 12,
    ) -> None:
        """Create a short cinematic video from a single image using Ken Burns motion."""
        print(f"🖼️ Building image-based video from: {image_path}")
        overlay_img = self._create_title_overlay(titulo, numero)

        # Gentle zoom-in + subtle pan to avoid static feeling.
        ken_burns_filter = (
            "[0:v]scale=2200:1238,"
            "zoompan=z='min(1.18,1+0.0007*on)':"
            "x='iw/2-(iw/zoom/2)+sin(on/30)*12':"
            "y='ih/2-(ih/zoom/2)+cos(on/37)*8':"
            "d=1:s=1920x1080:fps=30,"
            "format=yuv420p[bg];"
            "[bg][2:v]overlay=enable='between(t,0,5)'[v]"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-t",
            str(duration_seconds),
            "-i",
            str(image_path),
            "-i",
            str(audio_path),
            "-i",
            str(overlay_img),
            "-filter_complex",
            ken_burns_filter,
            "-map",
            "[v]",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ ffmpeg image-video encode failed: {result.stderr}")
        else:
            print(f"✅ Image-based video created: {output_path}")

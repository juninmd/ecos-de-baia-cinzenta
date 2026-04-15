#!/usr/bin/env python3
"""
Animated Video Generator with Enhanced Effects
Creates dynamic videos with story-driven animations.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess
from typing import List, Tuple
import random
import numpy as np


class AnimatedVideoComposer:
    """Creates animated videos with dynamic effects based on narrative."""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(exist_ok=True)
        self._vignette_cache = {}
        self._vignette_mask = None
        self._black_bg = None

        # Load fonts once
        try:
            self.font_title = ImageFont.truetype("arial.ttf", 80)
            self.font_subtitle = ImageFont.truetype("arial.ttf", 50)
        except:
            self.font_title = ImageFont.load_default()
            self.font_subtitle = ImageFont.load_default()
    
    def create_animated_sequence(
        self,
        image_paths: List[Path],
        duration: float,
        titulo: str,
        numero: str,
        output_path: Path,
        audio_path: Path
    ):
        """
        Create animated video sequence with multiple images and dynamic effects.
        
        Effects:
        - Ken Burns: Zoom + Pan on each image
        - Crossfade: Smooth transitions between scenes
        - Rain overlay (noir aesthetic)
        - Dynamic title with glow effect
        """
        fps = 24
        total_frames = int(duration * fps)
        width, height = 1920, 1080
        num_images = len(image_paths)
        
        # Calculate timing
        frames_per_image = total_frames / num_images
        crossfade_frames = int(fps * 1.5)  # 1.5s crossfade
        
        print(f"🎨 Creating animated sequence with {num_images} images ({total_frames} total frames)...")
        
        # Generate frames
        frames_dir = self.temp_dir / 'frames'
        frames_dir.mkdir(exist_ok=True)
        
        # Pre-load images (limit to 10 to avoid memory issues)
        loaded_images = []
        for p in image_paths[:10]:
            if p and p.exists():
                loaded_images.append(Image.open(p).convert('RGB'))
            else:
                img = Image.new('RGB', (2200, 1400), color=(10, 15, 25))
                self._add_gradient_overlay(img, color1=(15, 20, 35), color2=(5, 10, 20))
                loaded_images.append(img)
        
        for frame_num in range(total_frames):
            progress = frame_num / total_frames
            
            # Determine which images to blend
            current_img_idx = int(frame_num / frames_per_image)
            next_img_idx = min(current_img_idx + 1, num_images - 1)
            
            # Local progress within the current image's duration
            img_start_frame = int(current_img_idx * frames_per_image)
            img_progress = (frame_num - img_start_frame) / frames_per_image
            
            # Create frame with zoom + pan for current image
            frame = self._create_scene_frame(
                loaded_images[current_img_idx], width, height, img_progress, frame_num
            )
            
            # Handle crossfade to next image
            frames_remaining_in_segment = int((current_img_idx + 1) * frames_per_image) - frame_num
            if frames_remaining_in_segment < crossfade_frames and current_img_idx < num_images - 1:
                fade_alpha = 1.0 - (frames_remaining_in_segment / crossfade_frames)
                
                # Progress for the next image (starting from 0)
                next_img_progress = (crossfade_frames - frames_remaining_in_segment) / frames_per_image
                next_frame = self._create_scene_frame(
                    loaded_images[next_img_idx], width, height, next_img_progress, frame_num
                )
                
                # Blend frames
                frame = Image.blend(frame, next_frame, fade_alpha)
            
            # Apply global overlays (Vignette, Rain, Title)
            self._apply_global_overlays(frame, frame_num, total_frames, titulo, numero)
            
            # Save frame
            frame.save(frames_dir / f'frame_{frame_num:05d}.png')
            
            if frame_num % 100 == 0:
                print(f"  Generated {frame_num}/{total_frames} frames...")
        
        print(f"✓ All frames generated")
        
        # Encode video with ffmpeg
        print("🎬 Encoding video...")
        self._encode_video_with_audio(frames_dir, audio_path, output_path, fps)
        
        # Cleanup pre-loaded images
        for img in loaded_images:
            img.close()
            
        print("✓ Video encoded")

    def _create_scene_frame(
        self,
        bg: Image.Image,
        width: int,
        height: int,
        progress: float,
        frame_num: int
    ) -> Image.Image:
        """Create single scene frame with zoom/pan."""
        # Ken Burns: gradual zoom unique to this segment
        zoom = 1.0 + (0.15 * progress)
        
        # Pan effect: slight drift
        pan_x = int(50 * progress)
        
        # Calculate crop
        source_w = int(width / zoom)
        source_h = int(height / zoom)
        
        crop_x = min(pan_x, bg.width - source_w)
        crop_y = max(0, int((bg.height - source_h) / 2))

        cropped = bg.crop((crop_x, crop_y, crop_x + source_w, crop_y + source_h))
        return cropped.resize((width, height), Image.Resampling.LANCZOS)

    def _apply_global_overlays(self, frame, frame_num, total_frames, titulo, numero):
        """Add noir effects and text overlays to a frame."""
        # Add noir vignette
        self._add_vignette(frame)
        
        # Add rain effect
        if frame_num % 3 == 0:
            self._add_rain_particles(frame)
        
        # Add title (fade in at start, stay 5s)
        title_duration = 5.0
        title_frames = int(title_duration * 24)
        if frame_num < title_frames:
            alpha = self._calculate_title_alpha(frame_num, title_frames)
            self._add_title_overlay(frame, titulo, numero, alpha)
    
    def _add_gradient_overlay(self, img: Image.Image, color1: Tuple[int, int, int], color2: Tuple[int, int, int]):
        """Add vertical gradient overlay."""
        # Use NumPy for vectorized gradient generation
        c1 = np.array(color1)
        c2 = np.array(color2)

        # Generate vertical gradient (H, 1)
        y = np.arange(img.height) / img.height

        # Calculate colors: shape (H, 3)
        gradient = (c1 + (c2 - c1) * y[:, None]).astype(np.uint8)

        # Reshape to (H, 1, 3) for 1-pixel wide column
        gradient = gradient.reshape((img.height, 1, 3))

        # Create image from array and resize to full width
        gradient_img = Image.fromarray(gradient, mode='RGB')
        gradient_img = gradient_img.resize((img.width, img.height), resample=Image.Resampling.NEAREST)

        # Paste efficiently
        img.paste(gradient_img)
        
    def _generate_vignette_mask(self, size):
        """Generate high-quality vignette mask using NumPy."""
        width, height = size
        y, x = np.ogrid[:height, :width]
        center_y, center_x = height / 2, width / 2
        max_dist_sq = (width / 2)**2 + (height / 2)**2
        dist_sq = (x - center_x)**2 + (y - center_y)**2
        
        # Calculate normalized radius (0 at center, 1 at corner)
        radius = np.sqrt(dist_sq) / np.sqrt(max_dist_sq)
        
        # Invert (1 at center, 0 at corner)
        mask = 1 - radius
        mask = np.clip(mask, 0, 1)

        # Apply curve (gamma correction for smoother/darker edges)
        mask = mask ** 1.5

        # Convert to 0-255
        mask_u8 = (mask * 255).astype(np.uint8)
        return Image.fromarray(mask_u8, mode="L")

    def _add_vignette(self, img: Image.Image):
        """Add dark vignette to edges (noir style)."""
        if self._vignette_mask is None or self._vignette_mask.size != img.size:
            self._vignette_mask = self._generate_vignette_mask(img.size)
            self._black_bg = Image.new("RGB", img.size, (0, 0, 0))

        # Apply vignette efficiently using cached mask
        result = Image.composite(img, self._black_bg, self._vignette_mask)
        img.paste(result)

    def _add_rain_particles(self, img: Image.Image):
        """Add subtle rain effect."""
        draw = ImageDraw.Draw(img, 'RGBA')
        
        for _ in range(50):  # 50 raindrops
            x = random.randint(0, img.width)
            y = random.randint(0, img.height)
            length = random.randint(10, 30)
            opacity = random.randint(50, 150)
            
            draw.line(
                [(x, y), (x + 2, y + length)],
                fill=(150, 180, 200, opacity),
                width=1
            )
    
    def _calculate_title_alpha(self, frame_num: int, total_title_frames: int) -> int:
        """Calculate title opacity for fade in/out."""
        fade_in_frames = 24  # 1 second
        fade_out_start = total_title_frames - 24
        
        if frame_num < fade_in_frames:
            return int(255 * (frame_num / fade_in_frames))
        elif frame_num > fade_out_start:
            return int(255 * ((total_title_frames - frame_num) / 24))
        else:
            return 255
    
    def _add_title_overlay(self, img: Image.Image, titulo: str, numero: str, alpha: int):
        """Add animated title with glow effect."""
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Title text
        title_text = f"CAPÍTULO {numero}"
        subtitle_text = titulo
        
        # Center position
        title_bbox = draw.textbbox((0, 0), title_text, font=self.font_title)
        title_w = title_bbox[2] - title_bbox[0]
        x_title = (img.width - title_w) // 2
        y_title = 100
        
        # Glow effect (multiple layers)
        glow_color = (0, 255, 255, alpha // 3)  # Cyan with transparency
        for offset in [4, 3, 2, 1]:
            draw.text(
                (x_title + offset, y_title + offset),
                title_text,
                font=self.font_title,
                fill=glow_color
            )
        
        # Main title (cyan)
        draw.text(
            (x_title, y_title),
            title_text,
            font=self.font_title,
            fill=(0, 255, 255, alpha)
        )
        
        # Subtitle (white, smaller)
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=self.font_subtitle)
        subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
        x_subtitle = (img.width - subtitle_w) // 2
        
        draw.text(
            (x_subtitle, y_title + 100),
            subtitle_text,
            font=self.font_subtitle,
            fill=(255, 255, 255, alpha)
        )
        
        # Composite overlay
        img_with_alpha = Image.new('RGBA', img.size)
        img_with_alpha.paste(img, (0, 0))
        img_with_alpha = Image.alpha_composite(img_with_alpha, overlay)
        img.paste(img_with_alpha.convert('RGB'))
    
    def _encode_video_with_audio(
        self,
        frames_dir: Path,
        audio_path: Path,
        output_path: Path,
        fps: int
    ):
        """Encode frames + audio into final video."""
        cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', str(frames_dir / 'frame_%05d.png'),
            '-i', str(audio_path),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',  # High quality
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            str(output_path)
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)

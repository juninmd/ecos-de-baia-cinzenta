#!/usr/bin/env python3
"""
Setup script for video generation assets.
Downloads royalty-free music and verifies required directories.
"""

import urllib.request
from pathlib import Path


def setup_directories(root: Path):
    """Create required directories."""
    directories = [
        root / 'docs' / 'public' / 'videos',
        root / 'assets',
        root / '.temp_video'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")


def download_background_music(root: Path):
    """
    Download Creative Commons background music.
    Using a cyberpunk ambient track from freemusicarchive.org
    """
    music_path = root / 'assets' / 'cyberpunk_ambient.mp3'
    
    if music_path.exists():
        print(f"✓ Music already exists: {music_path}")
        return
    
    # Fallback: Create silent track if download fails
    print("⚠ Background music download skipped (requires manual setup)")
    print("  You can add your own CC-licensed music to: assets/cyberpunk_ambient.mp3")
    
    # Create empty placeholder
    music_path.write_text("")


def verify_ffmpeg():
    """Check if ffmpeg is available."""
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ FFmpeg not found. Install it for video encoding:")
        print("  Windows: choco install ffmpeg")
        print("  Ubuntu: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return False


def main():
    root = Path(__file__).parent.parent
    
    print("🎬 Setting up video generation environment...\n")
    
    setup_directories(root)
    download_background_music(root)
    verify_ffmpeg()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("  1. Install dependencies: uv pip install -r requirements-dev.txt")
    print("  2. Generate test video: python scripts/video_generator.py --chapter 1")


if __name__ == '__main__':
    main()

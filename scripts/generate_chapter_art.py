import argparse
import os
import sys

# Import refactored modules
from art_gen.config import MODEL_ALTERNATIVES, print_alternatives
from art_gen.character_db import CharacterDatabase

from art_gen.chapter_context import ChapterContext
from art_gen.ollama_client import OllamaClient
from art_gen.image_generator import ImageGenerator


def validate_environment():
    """Validates the availability of required libraries and hardware for art generation."""
    print("🔍 Validating environment for Art Generation...")

    # Check Imports
    try:
        import requests
        print(f"   - Requests: ✅ {requests.__version__}")
    except ImportError:
        print("   - Requests: ❌ Not Found (Required for API)")

    try:
        import torch
        print(f"   - Torch: ✅ {torch.__version__}")
        cuda_ok = torch.cuda.is_available()
        print(f"   - CUDA Available: {'✅ Yes' if cuda_ok else '⚠️ No (CPU only)'}")
        if cuda_ok:
            print(f"     - Device: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("   - Torch: ❌ Not Found")

    try:
        import diffusers
        print(f"   - Diffusers: ✅ {diffusers.__version__}")
    except ImportError:
        print("   - Diffusers: ❌ Not Found")

    # Check Environment Variables
    api_url = os.environ.get("SD_API_URL")
    print(f"   - SD_API_URL: {api_url if api_url else '⚠️ Not set (Using local fallback)'}")

    fallback = os.environ.get("ART_ALLOW_CPU_FALLBACK")
    print(f"   - ART_ALLOW_CPU_FALLBACK: {fallback if fallback else 'Default (0)'}")

    print("\n✅ Validation complete.")


def _resolve_chapter_path(chapter_arg):
    """Finds the correct path for the given chapter file."""
    if os.path.exists(chapter_arg):
        return chapter_arg

    public_path = os.path.join("docs/public", chapter_arg)
    if os.path.exists(public_path):
        return public_path

    docs_path = os.path.join("docs", chapter_arg)
    if os.path.exists(docs_path):
        return docs_path

    print(f"❌ Error: Chapter file not found for input: {chapter_arg}")
    sys.exit(1)


def _should_skip_generation(chapter, output_path, force):
    """Determines if image generation should be skipped based on existing files or frontmatter."""
    image_exists_on_disk = os.path.exists(output_path)
    image_in_frontmatter = 'image:' in (chapter.frontmatter or "")

    if (image_exists_on_disk or image_in_frontmatter) and not force:
        print(f"⏭️ Skipping generation for {chapter.filepath}")
        if image_exists_on_disk:
            print(f"   - Image file exists: {output_path}")
        if image_in_frontmatter:
            print("   - Frontmatter has image reference")
        print("   Use --force to regenerate.")
        return True
    return False


def _generate_fallback_prompt(active_chars, style):
    """Generates a fallback prompt when Ollama is unavailable."""
    char_bits = ", ".join([f"{c['name']} ({c['description'][:110]})" for c in active_chars[:3]])
    return (
        f"cinematic chapter illustration, {style}, rain-soaked noir city, intense dramatic moment, "
        f"consistent character canon: {char_bits}, dynamic composition, high detail, "
        "ultra cinematic, noir cyberpunk, volumetric rain, film grain, masterpiece"
    )


def _setup_arg_parser():
    parser = argparse.ArgumentParser(description="Automated Chapter Art Generator")
    parser.add_argument('--chapter', required=False, help="Path to chapter markdown file")
    parser.add_argument(
        '--style',
        default="neo-noir cyberpunk, dramatic lighting, rainy atmosphere, realistic textures",
        help="Art style"
    )
    parser.add_argument('--ollama-model', default=os.environ.get('OLLAMA_MODEL', 'llama3.1:8b'), help="Ollama model")
    parser.add_argument(
        '--model-family',
        default=os.environ.get('ART_MODEL_FAMILY', 'sdxl'),
        choices=MODEL_ALTERNATIVES.keys(),
        help="Open source image model family"
    )
    parser.add_argument('--dry-run', action='store_true', help="Skip image generation")
    parser.add_argument('--list-alternatives', action='store_true', help="List open source alternatives and exit")
    parser.add_argument('--force', action='store_true', help="Force regeneration even if image exists")
    parser.add_argument('--validate', action='store_true', help="Validate environment and dependencies then exit")
    return parser


def process_chapter_worker(chapter_path_str, style, ollama_model, model_family, force, dry_run, db):
    chapter_path = _resolve_chapter_path(chapter_path_str)
    print(f"📖 Reading chapter: {chapter_path}")
    chapter = ChapterContext(chapter_path)

    base_name = os.path.basename(chapter_path).replace('.md', '.jpg').replace('-', '_')
    output_path = os.path.join("docs/public", base_name)

    if _should_skip_generation(chapter, output_path, force):
        return True

    active_chars = db.find_characters_in_text(chapter.body)
    print(f"👥 Characters detected: {[c['name'] for c in active_chars]}")

    ollama = OllamaClient(model=ollama_model)
    if not ollama.check_connection():
        print(f"⚠️ Cannot connect to Ollama at {ollama.host}. Using fallback prompt.")
        prompt = _generate_fallback_prompt(active_chars, style)
    else:
        prompt = ollama.generate_prompt(chapter.body, active_chars, style)

    if not prompt:
        print("❌ Failed to generate prompt.")
        return False

    print(f"\n🎨 Generated Prompt:\n{prompt}\n")

    generator = ImageGenerator(model_family=model_family)
    success = generator.generate(prompt, output_path, dry_run=dry_run)

    if success and not dry_run:
        chapter.update_frontmatter(f"/{base_name}")

    return success

def process_chapter(args, db):
    """Handles the core logic of processing a chapter for art generation."""
    success = process_chapter_worker(args.chapter, args.style, args.ollama_model, args.model_family, args.force, args.dry_run, db)
    if not success:
        sys.exit(1)


def main():
    parser = _setup_arg_parser()
    args = parser.parse_args()

    if args.list_alternatives:
        print_alternatives()
        return

    if args.validate:
        validate_environment()
        return

    if not args.chapter:
        parser.error("--chapter is required unless --list-alternatives or --validate is used")

    project_root = os.getcwd()
    char_file = os.path.join(project_root, "docs/personagens.md")
    db = CharacterDatabase(char_file)

    process_chapter(args, db)


if __name__ == "__main__":
    main()

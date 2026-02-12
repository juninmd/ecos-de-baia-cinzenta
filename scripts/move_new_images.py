import os
import shutil
import argparse
from pathlib import Path

def move_images(artifact_dir, output_dir):
    artifact_path = Path(artifact_dir)
    output_path = Path(output_dir)

    if not artifact_path.exists():
        print(f"Error: Artifact directory does not exist: {artifact_path}")
        return

    output_path.mkdir(parents=True, exist_ok=True)

    mapping = {
        "clara_moretti_sister": "clara.png",
        "enzo_sofia_rossi_pizza": "enzo_sofia.png",
        "helena_moretti_memory": "helena.png"
    }

    found_any = False
    for src in artifact_path.glob("*.png"):
        basename = src.name
        for key, new_name in mapping.items():
            if key in basename:
                dst = output_path / new_name
                shutil.copy2(src, dst)
                print(f"Copied {src} to {dst}")
                found_any = True

    if not found_any:
        print(f"No matching images found in {artifact_path}")

def main():
    parser = argparse.ArgumentParser(description="Move new character images from artifact directory to project directory.")
    parser.add_argument("--artifact-dir", help="Path to the artifact directory containing new images.")
    parser.add_argument("--output-dir", help="Path to the destination directory (default: docs/public/personagens).")

    args = parser.parse_args()

    # Priority: Command line arg > Environment variable
    artifact_dir = args.artifact_dir or os.environ.get("ARTIFACT_DIR")

    # For output_dir, we default to docs/public/personagens relative to the project root
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    default_output_dir = project_root / "docs" / "public" / "personagens"

    output_dir = args.output_dir or os.environ.get("OUTPUT_DIR") or default_output_dir

    if not artifact_dir:
        print("Error: Artifact directory must be specified via --artifact-dir or ARTIFACT_DIR environment variable.")
        return

    move_images(artifact_dir, output_dir)

if __name__ == "__main__":
    main()

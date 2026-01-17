import os
import sys

def verify_links():
    links_to_verify = [
        ("docs/capitulo-1.md", "capitulo-1"),
        ("docs/lore-do-livro.md", "lore-do-livro")
    ]

    # Also check all chapters mentioned in sidebar
    # But for now, let's just check the ones modified in index.md actions

    errors = []

    # Check if files exist
    for filepath, link in links_to_verify:
        if not os.path.exists(filepath):
            errors.append(f"File {filepath} does not exist for link {link}")

    if errors:
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("All key links verified.")

if __name__ == "__main__":
    verify_links()

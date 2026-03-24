import os
import re
import pytest
from pathlib import Path

# Base directory for documentation
DOCS_DIR = Path("docs")
PUBLIC_DIR = DOCS_DIR / "public"

def get_markdown_files():
    """Returns a list of all markdown files in the docs directory."""
    if not DOCS_DIR.exists():
        return []
    return list(DOCS_DIR.rglob("*.md"))

# Compile regex at module level for performance
LINK_REGEX = re.compile(r'\]\(((?:[^)(]|\([^)(]*\))*)\)')
IGNORE_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "tel:")

def extract_links(content):
    """Extracts all links from markdown content."""
    # Matches standard markdown links [text](link) and images ![text](link)
    # capture group 1 is the link url
    # Modified regex to handle balanced parentheses in URLs (one level deep)
    # e.g. [text](image(1).png)
    return LINK_REGEX.findall(content)

@pytest.mark.parametrize("file_path", get_markdown_files())
def test_links_in_file(file_path):
    """Checks that all local links in a markdown file point to existing files."""
    content = file_path.read_text(encoding="utf-8")
    links = extract_links(content)

    for link in links:
        # Clean the link (remove query params, title text etc if present)
        # Markdown link can be "url 'title'", we need just url
        link = link.split()[0]

        # Ignore external links, mailto, etc.
        if link.startswith(IGNORE_PREFIXES):
            continue

        # Ignore pure anchors
        if link.startswith("#"):
            continue

        # Split anchor from path
        link_path_str = link.split("#")[0]

        # If link was just "#anchor", link_path_str is empty
        if not link_path_str:
            continue

        # Handle Absolute paths (starting with /)
        if link_path_str.startswith("/"):
            # In VitePress, '/' usually resolves to the 'docs' directory or 'public'
            # We check both locations

            # 1. Check relative to docs root
            path_rel_to_docs = link_path_str.lstrip("/")
            target_in_docs = DOCS_DIR / path_rel_to_docs

            # 2. Check in public directory (assets often referenced as /image.png which maps to docs/public/image.png)
            target_in_public = PUBLIC_DIR / path_rel_to_docs

            exists = target_in_docs.exists() or target_in_public.exists()

            # Handle clean URLs or directory links (e.g. /guide/ points to /guide/index.md)
            if not exists and not target_in_docs.suffix:
                 if (target_in_docs / "index.md").exists():
                     exists = True

            assert exists, f"Broken absolute link in {file_path}: {link} -> Checked {target_in_docs} and {target_in_public}"

        else:
            # Relative paths
            target = (file_path.parent / link_path_str).resolve()

            # Check existence
            if target.exists():
                continue

            # If failed, maybe it is a directory link implying index.md
            if (target / "index.md").exists():
                continue

            # Special case: VitePress sometimes allows omitting extension for .md?
            # Usually better to be explicit, but let's check if .md exists
            if not target.suffix and target.with_suffix(".md").exists():
                continue

            assert False, f"Broken relative link in {file_path}: {link} -> Resolved to {target}"

import os
import re
import pytest

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

def get_markdown_files():
    markdown_files = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    return markdown_files

def resolve_link(current_file, link):
    # Remove anchor
    link = link.split('#')[0]

    if not link:
        return True # Just an anchor

    if link.startswith('http://') or link.startswith('https://') or link.startswith('mailto:'):
        return True # External link, ignore for now

    # Check for static assets in public folder (often referenced as /image.png)
    # VitePress maps / to public/ as well for assets, but for markdown links checking relative to docs root is safer for checking file existence.

    target_path = None

    if link.startswith('/'):
        # Absolute path relative to docs root
        # e.g. /foo/bar -> docs/foo/bar
        target_path = os.path.join(DOCS_DIR, link.lstrip('/'))
    else:
        # Relative path
        target_path = os.path.join(os.path.dirname(current_file), link)

    # Clean path
    target_path = os.path.normpath(target_path)

    # Check if file exists
    if os.path.exists(target_path):
        return True

    # Try with .md extension if missing
    if os.path.exists(target_path + '.md'):
        return True

    # Try as directory (implies index.md)
    if os.path.isdir(target_path):
         if os.path.exists(os.path.join(target_path, 'index.md')):
             return True

    # Handle VitePress "pretty" links where foo -> foo.md
    # If target_path ends with 'foo', try 'foo.md'
    # Use dirname and basename
    dir_name = os.path.dirname(target_path)
    base_name = os.path.basename(target_path)

    # If checking for 'foo', and 'foo.md' exists in that dir
    candidate = os.path.join(dir_name, base_name + '.md')
    if os.path.exists(candidate):
        return True

    # Also check public directory for assets (images, etc)
    # docs/public is mapped to /
    if link.startswith('/'):
         public_path = os.path.join(DOCS_DIR, 'public', link.lstrip('/'))
         if os.path.exists(public_path):
             return True
         # Also try without leading slash relative to current file? No, / implies root.

    return False

@pytest.mark.parametrize("filepath", get_markdown_files())
def test_internal_links(filepath):
    """
    Parses a markdown file and checks if all internal links are valid.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find [text](link)
    # This is a simple regex and might fail on nested brackets, but sufficient for most markdown
    links = re.findall(r'\[.*?\]\((.*?)\)', content)

    broken_links = []

    for link in links:
        # Filter out some common non-file links
        if not resolve_link(filepath, link):
             broken_links.append(link)

    assert not broken_links, f"Broken links found in {os.path.relpath(filepath, DOCS_DIR)}: {broken_links}"

import os
import re
from pathlib import Path

# Compile regex at module level for performance
IMAGE_FRONTMATTER_RE = re.compile(r'image:.*')

class ChapterContext:
    def __init__(self, filepath):
        # Determine if filepath is a Path or just string
        self.filepath = Path(filepath) if isinstance(filepath, str) else filepath
        self._content = None
        self._frontmatter = None
        self._body = None

    def _load(self):
        # We need to support mock_open testing which hooks open() instead of pathlib
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Chapter file not found: {self.filepath}")

        with open(self.filepath, 'r', encoding='utf-8') as f:
            self._content = f.read()

        if self._content.startswith("---"):
            parts = self._content.split("---", 2)
            if len(parts) >= 3:
                self._frontmatter = parts[1]
                self._body = parts[2]
                return
        self._body = self._content
        self._frontmatter = ""

    @property
    def content(self):
        if self._content is None:
            self._load()
        return self._content

    @property
    def frontmatter(self):
        if self._frontmatter is None:
            self._load()
        return self._frontmatter

    @frontmatter.setter
    def frontmatter(self, value):
        self._frontmatter = value

    @property
    def body(self):
        if self._body is None:
            self._load()
        return self._body

    def update_frontmatter(self, image_path):
        """Updates or adds the image reference in the frontmatter."""
        public_path = image_path if image_path.startswith("/") else f"/{os.path.basename(image_path)}"

        if self.frontmatter:
            if "image:" in self.frontmatter:
                self.frontmatter = IMAGE_FRONTMATTER_RE.sub(f"image: {public_path}", self.frontmatter)
            else:
                self.frontmatter = self.frontmatter.rstrip() + f"\nimage: {public_path}\n"
        else:
            self.frontmatter = f"\nimage: {public_path}\n"

        new_content = f"---{self.frontmatter}---{self.body}"
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated frontmatter in {self.filepath}")

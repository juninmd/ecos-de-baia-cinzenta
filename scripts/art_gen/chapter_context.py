import os
import re
import sys


class ChapterContext:
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = ""
        self.frontmatter = ""
        self.body = ""
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Error: Chapter file not found at {self.filepath}")

        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.content = f.read()

        self._parse_content()

    def _parse_content(self):
        """Parses content to separate frontmatter from body."""
        if self.content.startswith('---'):
            parts = self.content.split('---', 2)
            if len(parts) >= 3:
                self.frontmatter = parts[1]
                self.body = parts[2]
                return

        # Fallback if no valid frontmatter block
        self.frontmatter = ""
        self.body = self.content

    def update_frontmatter(self, image_path):
        """Updates or adds the image reference in the frontmatter."""
        public_path = image_path if image_path.startswith('/') else '/' + os.path.basename(image_path)

        if self.frontmatter:
            if 'image:' in self.frontmatter:
                self.frontmatter = re.sub(r'image:.*', f'image: {public_path}', self.frontmatter)
            else:
                self.frontmatter = self.frontmatter.rstrip() + f'\nimage: {public_path}\n'
        else:
            self.frontmatter = f'\nimage: {public_path}\n'

        new_content = f'---{self.frontmatter}---{self.body}'
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated frontmatter in {self.filepath}")

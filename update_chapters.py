import os
import re

# Map of specific chapters to specific images
image_map = {
    'capitulo-1.md': '/gabo.webp',
    'capitulo-2.md': '/gabo-compra-cafe.jpeg',
    'capitulo-3.md': '/delegacia.jpeg',
    'capitulo-4.md': '/elite.jpg',
    'capitulo-5.md': '/beco.jpeg',
    'capitulo-17.md': '/gabo-arma.jpeg',
    'capitulo-18.md': '/gabo-cansado.jpeg',
    'capitulo-21.md': '/livia.jpg',
    'capitulo-23.md': '/cidade.jpg',
    'capitulo-46.md': '/gabo-compra-cafe.jpeg'
}

default_image = '/cidade.jpg'
docs_dir = 'docs'

# Get all chapter files
files = [f for f in os.listdir(docs_dir) if f.startswith('capitulo-') and f.endswith('.md')]

for filename in files:
    filepath = os.path.join(docs_dir, filename)

    # Determine which image to use
    image_to_use = image_map.get(filename, default_image)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if frontmatter exists (starts with ---)
    if content.startswith('---'):
        # Check if image property already exists
        if 'image:' not in content.split('---')[1]:
            # Insert image property into existing frontmatter
            # Find the end of the frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]

                # Add image to frontmatter
                new_frontmatter = frontmatter.rstrip() + f'\nimage: {image_to_use}\n'
                new_content = f'---{new_frontmatter}---{body}'

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filename} with image {image_to_use}")
    else:
        # Create frontmatter if it doesn't exist (unlikely for chapters but possible)
        new_content = f'---\nimage: {image_to_use}\n---\n{content}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Created frontmatter for {filename}")

print("Done updating chapters.")

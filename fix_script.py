import sys

with open('scripts/local_art_gen.py', 'r') as f:
    content = f.read()

content = content.replace('''try:
    from dotenv import load_dotenv

except ImportError:
    pass''', '''try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass''')

with open('scripts/local_art_gen.py', 'w') as f:
    f.write(content)

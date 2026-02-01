# Copilot Instructions - Ecos de Baía Cinzenta

## Project Overview
This is an AI-collaborative cyberpunk noir novel published as an interactive VitePress website. The AI agent "Jules" writes daily chapters, supervised by Antonio Carlos. The codebase includes both content (story) and tooling (video generation, image management, TTS).

## Architecture

### Dual Stack
- **Frontend (Node.js)**: VitePress static site with custom TTS player and Terminal UI
  - Config: [docs/.vitepress/config.js](docs/.vitepress/config.js)
  - Theme: `docs/.vitepress/theme/` (custom components)
  - Deploy: Netlify (automated via `netlify.toml`)

- **Backend (Python)**: Content generation scripts
  - Dependency manager: `uv` (NOT pip) - see [AGENTS.md](AGENTS.md)
  - Primary scripts: `scripts/` (video generation, image sync)
  - Tools: `tools/` (prompt generation for AI characters)

### Chapter Structure
Each chapter is markdown with YAML frontmatter:
```markdown
---
image: /capitulo_1.jpg
---
# Capítulo 1: Olhos de Vidro
```
- Files: `docs/capitulo-{1-114}.md`
- Images: `docs/public/*.{jpg,jpeg,webp}`
- Mapping: Controlled by `update_chapters.py`

## Development Workflows

### Node.js Tasks
```bash
pnpm install          # Install dependencies (NOT npm)
pnpm docs:dev         # Dev server at localhost:5173
pnpm docs:build       # Build for production
pnpm test             # Run pytest (yes, pytest for Node project!)
```

### Python Setup (CRITICAL)
```bash
uv venv                              # Create venv (NOT python -m venv)
.venv\Scripts\activate               # Windows activation
uv pip install -r requirements.txt  # Install deps
```

### Video Generation
```bash
# Generate cinematic video for chapter
python scripts/video_generator.py --chapter 1

# Automated via .github/workflows/video-generation.yml
# Output: docs/public/videos/capitulo_*.mp4
```

### Testing
- Test location: `tests/` (Python) + inline in `scripts/`
- Run: `pnpm test` (executes pytest)
- Focus: Link validation ([tests/test_links.py](tests/test_links.py))

## Project-Specific Conventions

### Content Rules
- **Lore Bible**: [docs/lore-do-livro.md](docs/lore-do-livro.md) defines the universe's "constitution" (Gray Bay setting, Aeterna Corp, drug "Lázaro", etc.)
- **Character Consistency**: Character visuals defined in [tools/prompt_generator.py](tools/prompt_generator.py) for AI image generation
- **Chapter Naming**: `capitulo-{N}.md` (Portuguese), NOT `chapter-{N}.md`

### Image Management
- Default image: `/cidade.jpg`
- Chapter-specific mappings: `update_chapters.py` (dict `image_map`)
- **Never** manually edit frontmatter; use `update_chapters.py` to batch update

### Docker Services
`docker-compose.yml` runs Ollama for local AI art generation:
```bash
docker-compose up -d  # Start Ollama service on port 11434
```

### VitePress Sidebar
Auto-generated from [docs/.vitepress/config.js](docs/.vitepress/config.js):
- Structure: Livro > Parte > Capítulo
- Example: "LIVRO 1: O DILÚVIO" → "Parte I: A Chuva" → chapters 1-4
- When adding chapters: Update `sidebar` array in config.js

## External Dependencies

### GitHub Actions
- **CI/CD**: `.github/workflows/ci.yml` - Tests + semantic-release
- **Video**: `.github/workflows/video-generation.yml` - Auto-generates videos
- **Art**: `.github/workflows/art_generation.yml` - Character artwork

### APIs & Services
- **Netlify**: Auto-deploys on push to main
- **Google Gemini**: Used by `scripts/` for AI tasks (require API key)
- **TTS**: Browser Web Speech API (no external service)

## Common Tasks

### Adding a New Chapter
1. Create `docs/capitulo-{N}.md` with frontmatter
2. Update sidebar in [docs/.vitepress/config.js](docs/.vitepress/config.js)
3. Run `python update_chapters.py` if image needed
4. GitHub Actions will auto-generate video

### Modifying Character Descriptions
Edit `CHARACTERS` dict in [tools/prompt_generator.py](tools/prompt_generator.py) - used by image generation pipelines.

### Debugging VitePress Build
- Check theme components in `docs/.vitepress/theme/`
- Custom TTS player logic embedded in theme
- Terminal UI uses `Ctrl+K` keybind

### Building Android App
```bash
pnpm icons:generate       # Generate app icons
pnpm android:sync         # Sync web build to Android
pnpm android:open         # Open in Android Studio
```
See [ANDROID.md](ANDROID.md) for PWA and native app details.

## AI Agent Context
- Agent name: **Jules** (daily chapter writer)
- Supervisor: **Antonio Carlos**
- Goal: Test AI's ability to maintain narrative coherence across 100+ chapters
- Review workflow: Jules opens PRs → Antonio reviews → Merge to main → Auto-deploy

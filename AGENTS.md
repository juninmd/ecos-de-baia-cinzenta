# AGENTS.md

## Development Environment
This project uses `uv` for Python dependency management.

### Setup
1. Install `uv`: `pip install uv` (or follow official docs)
2. Create virtual environment:
   ```bash
   uv venv
   ```
3. Activate virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   uv pip install -r requirements-dev.txt
   ```

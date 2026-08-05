# 🗺️ ROADMAP.md - Meu Livro

## 1. Vision & Goals
**Vision:** To build a high-performance, immersive reading platform ("Meu Livro") that blends a compelling cyberpunk noir narrative with cutting-edge automated pipelines.
**Goals:**
- Deliver a seamless reading experience optimized for speed and low resource usage using modern Node.js/TypeScript and VitePress.
- Adhere strictly to the Antigravity protocol (150-line file limits, strict typing, clean architecture).
- Automate narrative enhancements, including AI-driven chapter art generation.
- Maintain a robust CI/CD pipeline ensuring zero regressions during frequent narrative updates.

## 2. Current Status
**Phase: Refinement & Depth (Phase 2)**
- **Completed:** Initial scaffolding, repository setup, basic architecture, and Antigravity documentation alignment.
- **In Progress:** Feature expansion (core business logic), increasing test coverage to >80%, and continuous narrative publishing (currently up to Chapter 168).
- **Recent Milestones:** Migration of narrative content to `docs/public/`, stabilization of automated art generation scripts, and CI/CD workflow updates for robust PR validation.

## 3. Quarterly Roadmap

### Q1: Narrative Stabilization & Test Coverage
- **High priority (bugs, critical features):**
  - Fix failing CI pipeline ([#180](https://github.com/juninmd/ecos-de-baia-cinzenta/issues/180)).
  - Synchronize `GEMINI.md` (Single Source of Truth) with narrative progress up to Chapter 168.
  - Consolidate all narrative chapters and analysis files within `docs/public/` to prevent CI/CD data-loss safeguard triggers.
  - Fix any flaky tests in the Python art generation script (e.g., CPU fallback validation).
- **Medium priority (enhancements, improvements):**
  - Increase automated test coverage for core VitePress build configurations and Node.js backend services.
- **Low priority (technical debt, optimizations):**
  - Refactor older logic modules to strictly adhere to the Antigravity 150-line limit.

### Q2: Enhanced Media & Frontend Polish
- **High priority (bugs, critical features):**
  - Stabilize the Stable Diffusion AI chapter art generation pipeline against API rate limits and external dependency conflicts.
- **Medium priority (enhancements, improvements):**
  - Implement dynamic frontend features in VitePress for a richer user reading experience (e.g., character index, interactive timeline).
- **Low priority (technical debt, optimizations):**
  - Clean up unused assets and optimize image formats for faster load times.

### Q3: Automation & Scale
- **High priority (bugs, critical features):**
  - Resolve cross-platform environment issues (Windows/Linux) in local development setups.
- **Medium priority (enhancements, improvements):**
  - Fully automate the release pipeline (CI/CD) for seamless production deployments.
  - Automate the update process for `docs/cronologia.md` based on new chapter metadata.
- **Low priority (technical debt, optimizations):**
- Audit and update third-party dependencies (`package.json`, `requirements-dev.txt`, `requirements-art.txt`) for security and performance.

### Q4: Global Launch & Community Features
- **High priority (bugs, critical features):**
  - Conduct final security and performance audits prior to v1.0 milestone release.
- **Medium priority (enhancements, improvements):**
  - Prepare for global launch: multi-language support scaffolding and community interaction features.
- **Low priority (technical debt, optimizations):**
  - Finalize comprehensive developer documentation and onboarding guides.

## 4. Feature Details

### Feature: AI Chapter Art Generation Pipeline
- **User Value Proposition:** Provides readers with immersive, automatically generated visual representations of key chapter moments without manual artist intervention.
- **Technical Approach:** Utilize a Python script (`scripts/generate_chapter_art.py`) triggered by GitHub Actions. The script reads chapter metadata and uses Stable Diffusion APIs (with local CPU fallback) to generate and save images.
- **Success Criteria:** 95% of new chapters successfully generate accompanying artwork within 5 minutes of PR merge, with zero disruption to the main VitePress build.
- **Estimated Effort:** Medium

### Feature: Interactive Narrative Frontend (VitePress)
- **User Value Proposition:** Enhances the reading experience by providing fast, accessible, and easily navigable story content.
- **Technical Approach:** Leverage VitePress to serve Markdown files statically. Customize the theme to match the cyberpunk noir aesthetic and add custom Vue components for interactive elements.
- **Success Criteria:** Page load times under 1 second, zero broken links across chapters, and successful deployment via Netlify.
- **Estimated Effort:** Large

## 5. Dependencies & Risks
- **External API Reliance:** The AI art generation depends on external Stable Diffusion APIs. *Mitigation:* The workflow is configured with `ART_ALLOW_CPU_FALLBACK: "true"` to prevent build failures when the API is unavailable.
- **Dependency Conflicts:** Python ML libraries (`diffusers`, `torch`) can conflict with other tools (e.g., `gtts`). *Mitigation:* Explicitly pin dependency versions (e.g., `typer<0.10.0`, `click<8.2`) in `requirements-art.txt` to isolate environments.
- **Antigravity Protocol Constraints:** The strict 150-line limit may increase the cognitive load of navigating deeply nested directories as the project scales. *Mitigation:* Maintain strict domain-driven organization and comprehensive architectural documentation.
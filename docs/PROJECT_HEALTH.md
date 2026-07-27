# Project Health

This document records the repository improvement pass applied on 2026-05-17.

## Detected Surface

- Node.js / TypeScript / JavaScript
- Python pyproject
- uv lockfile
- Docker
- Docker Compose
- GitHub Actions

## Automation Added Or Confirmed

- Security policy: Added in this pass.
- Dependabot: Added in this pass.
- EditorConfig: Already present before this pass.
- Project Health workflow: Existing workflows were present; added a dedicated Project Health workflow.
- Pull request quality checklist: Added in this pass.

## Available Root Commands

- package script: android:add
- package script: android:build
- package script: android:init
- package script: android:open
- package script: android:run
- package script: android:sync
- package script: build:sw
- package script: docs:build
- package script: docs:dev
- package script: docs:preview
- package script: icons:generate
- python script: local-art-gen
- python script: local-art-gen
- package script: test
- python script: video-gen
- python script: video-gen

## Improvement Plan

1. Keep dependency drift visible through weekly Dependabot pull requests.
2. Keep runtime secrets out of git through the Project Health guardrail.
3. Use .editorconfig to reduce formatting churn across agents and local editors.
4. Treat this file as the lightweight audit entry for future improvements.

## Suggested Next Improvements

- Add project-specific tests to the Project Health workflow once the default branch is stable.
- Add CodeQL or language-native security scanning where the repository has a supported build path.
- Convert manual setup notes into reproducible scripts when setup steps are repeated.
- Add structured logging and health endpoints to service repositories that expose long-running APIs.

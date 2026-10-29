#!/usr/bin/env python3
"""
Test PWA configuration and validate manifest/service worker.
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC = REPO_ROOT / "docs" / "public"


def _manifest():
    return json.loads((PUBLIC / "manifest.json").read_text(encoding="utf-8"))


def test_manifest_campos_obrigatorios():
    manifest = _manifest()
    for field in ["name", "short_name", "start_url", "display", "icons"]:
        assert field in manifest, f"manifest.json sem o campo {field}"
    assert manifest["display"] == "standalone"


def test_manifest_icones_existem():
    for icon in _manifest()["icons"]:
        assert (PUBLIC / icon["src"].lstrip("/")).is_file(), f"ícone ausente: {icon['src']}"


def test_service_worker_handlers():
    content = (REPO_ROOT / "docs" / "sw.ts").read_text(encoding="utf-8")
    for feature in ["addEventListener('install'", "addEventListener('fetch'", "caches.open"]:
        assert feature in content, f"service worker sem {feature}"


def test_offline_page_existe():
    assert (PUBLIC / "offline.html").is_file(), "offline.html ausente"


def test_android_aponta_para_site_publicado_em_https():
    config = json.loads((REPO_ROOT / "capacitor.config.json").read_text(encoding="utf-8"))
    assert config["server"]["url"] == "https://juninmd.github.io/ecos-de-baia-cinzenta/"
    assert config["server"].get("cleartext") is False

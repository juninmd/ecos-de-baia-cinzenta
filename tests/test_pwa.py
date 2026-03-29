#!/usr/bin/env python3
"""
Test PWA configuration and validate manifest/service worker.
"""

import json
from pathlib import Path

def test_manifest():
    """Validate manifest.json structure."""
    manifest_path = Path("docs/public/manifest.json")

    if not manifest_path.exists():
        print("❌ manifest.json not found!")
        return False

    with open(manifest_path) as f:
        manifest = json.load(f)

    required_fields = ["name", "short_name", "start_url", "display", "icons"]

    for field in required_fields:
        if field not in manifest:
            print(f"❌ Missing required field: {field}")
            return False

    print(f"✓ manifest.json is valid")
    print(f"  Name: {manifest['name']}")
    print(f"  Icons: {len(manifest['icons'])} sizes")

    # Validate icons exist
    icons_dir = Path("docs/public/icons")
    missing_icons = []

    for icon in manifest['icons']:
        icon_path = Path("docs/public") / icon['src'].lstrip('/')
        if not icon_path.exists():
            missing_icons.append(icon['src'])

    if missing_icons:
        print(f"❌ Missing icon files: {missing_icons}")
        return False

    print(f"✓ All {len(manifest['icons'])} icon files exist")
    return True

def test_service_worker():
    """Validate service worker exists."""
    sw_path = Path("docs/sw.ts")

    if not sw_path.exists():
        print("❌ sw.ts not found!")
        return False

    content = sw_path.read_text()

    # Check for essential SW features
    required_features = [
        "addEventListener('install'",
        "addEventListener('fetch'",
        "caches.open"
    ]

    for feature in required_features:
        if feature not in content:
            print(f"❌ Service worker missing: {feature}")
            return False

    print("✓ Service worker is valid")
    return True

def test_offline_page():
    """Validate offline page exists."""
    offline_path = Path("docs/public/offline.html")

    if not offline_path.exists():
        print("❌ offline.html not found!")
        return False

    print("✓ Offline page exists")
    return True

if __name__ == "__main__":
    print("🧪 Testing PWA Configuration")
    print("=" * 50)

    results = [
        test_manifest(),
        test_service_worker(),
        test_offline_page()
    ]

    if all(results):
        print("\n✅ All PWA tests passed!")
        print("\n📱 Ready to install as PWA:")
        print("   1. Build: pnpm docs:build")
        print("   2. Deploy: Git push (auto-deploys to Netlify)")
        print("   3. Visit: https://ecos-de-baia-cinzenta.netlify.app")
        print("   4. Chrome menu → 'Add to Home screen'")
    else:
        print("\n❌ Some tests failed. Fix errors above.")
        exit(1)

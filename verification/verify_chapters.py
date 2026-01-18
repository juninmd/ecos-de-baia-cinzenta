from playwright.sync_api import sync_playwright, expect
import time

def verify_chapters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Chapter 47
        print("Navigating to Chapter 47...")
        page.goto("http://localhost:5173/capitulo-47")
        page.wait_for_selector("h1")
        expect(page.get_by_role("heading", name="Capítulo 47: Quebra de Ossos")).to_be_visible()
        # Use first=True to avoid strict mode error, just verifying content presence
        expect(page.get_by_text("O Taxidermista").first).to_be_visible()
        page.screenshot(path="verification/chapter_47.png")
        print("Chapter 47 verified.")

        # Chapter 48
        print("Navigating to Chapter 48...")
        page.goto("http://localhost:5173/capitulo-48")
        page.wait_for_selector("h1")
        expect(page.get_by_role("heading", name="Capítulo 48: Fantasma na Máquina")).to_be_visible()
        expect(page.get_by_text("Valéria").first).to_be_visible()
        page.screenshot(path="verification/chapter_48.png")
        print("Chapter 48 verified.")

        # Chapter 49
        print("Navigating to Chapter 49...")
        page.goto("http://localhost:5173/capitulo-49")
        page.wait_for_selector("h1")
        expect(page.get_by_role("heading", name="Capítulo 49: A Isca Perfeita")).to_be_visible()
        expect(page.get_by_text("A Isca Perfeita").first).to_be_visible()
        page.screenshot(path="verification/chapter_49.png")
        print("Chapter 49 verified.")

        browser.close()

if __name__ == "__main__":
    verify_chapters()

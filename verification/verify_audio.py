
from playwright.sync_api import sync_playwright

def verify_audio_player():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a larger viewport to ensure sidebar and content are visible
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Navigate to a chapter page where the player should be visible
        # Assuming port 5173 is standard for vite, check log if fails
        page.goto("http://localhost:5173/capitulo-1")

        # Wait for the player to be visible
        # We look for the "Ouvir Capítulo" button
        page.wait_for_selector(".audio-player", state="visible")

        # Take a screenshot
        page.screenshot(path="verification/audio_player.png")

        browser.close()

if __name__ == "__main__":
    verify_audio_player()

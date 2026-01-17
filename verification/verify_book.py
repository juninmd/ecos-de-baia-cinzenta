
from playwright.sync_api import sync_playwright

def verify_chapters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Navigate to local server
            page.goto("http://localhost:5173")

            # Wait for content
            page.wait_for_selector("h1")

            # Navigate to one of the new action chapters
            page.goto("http://localhost:5173/capitulo-34")
            page.wait_for_selector("h1")

            # Take screenshot of the RPG scene
            page.screenshot(path="verification/cap34_rpg.png", full_page=True)

            # Navigate to the ending
            page.goto("http://localhost:5173/capitulo-44")
            page.wait_for_selector("h1")
            page.screenshot(path="verification/cap44_end.png", full_page=True)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_chapters()

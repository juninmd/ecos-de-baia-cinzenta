
from playwright.sync_api import sync_playwright

def verify_chapter_45():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Navigate to local server
            page.goto("http://localhost:5173/capitulo-45")

            # Wait for content
            page.wait_for_selector("h1")

            # Verify Title
            header = page.locator("h1").inner_text()
            if "Capítulo 45: O Despertar" in header:
                print("Successfully navigated to Chapter 45")
            else:
                 print(f"Failed, header is: {header}")

            # Take screenshot
            page.screenshot(path="verification/cap45.png", full_page=True)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_chapter_45()

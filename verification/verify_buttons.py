
from playwright.sync_api import sync_playwright

def verify_buttons():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Navigate to local server
            page.goto("http://localhost:5173")

            # Wait for content
            page.wait_for_selector("h1")

            # Click "Começar a Leitura" and verify URL
            # Note: The URL might not change exactly to what we expect if there's a redirect or slash handling,
            # so we check if we end up on the right page content.
            page.get_by_role("link", name="Começar a Leitura").click()

            # Wait for the H1 of Chapter 1
            page.wait_for_selector("h1")
            header = page.locator("h1").inner_text()
            if "Capítulo 1" in header:
                print("Successfully navigated to Chapter 1")
            else:
                 print(f"Failed to navigate to Chapter 1, found header: {header}")

            # Go back
            page.go_back()
            page.wait_for_selector("h1")

            # Click "Sobre o Universo" and verify URL
            page.get_by_role("link", name="Sobre o Universo").click()

             # Wait for the H1 of Lore
            page.wait_for_selector("h1")
            header_lore = page.locator("h1").inner_text()

            if "Universo Literário" in header_lore or "Lore" in header_lore:
                print("Successfully navigated to Lore")
            else:
                print(f"Failed to navigate to Lore, found header: {header_lore}")


            # Take screenshot of the Lore page to confirm
            page.screenshot(path="verification/lore_page.png", full_page=True)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_buttons()

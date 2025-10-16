from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Capture console logs
    page.on("console", lambda msg: print(f"Browser console: {msg.text}"))

    # 1. Arrange: Go to the app's homepage.
    page.goto("http://localhost:3000")

    # 2. Act: Create a new game.
    page.get_by_placeholder("Scenario").fill("A group of adventurers find themselves in a dark cave.")
    page.get_by_placeholder("Password (optional)").fill("password123")
    page.get_by_role("button", name="Create Game").click()

    # 3. Assert: Check that the game was created.
    page.wait_for_selector("text=Join Game")

    # 4. Screenshot: Capture the result.
    page.screenshot(path="jules-scratch/verification/verification.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
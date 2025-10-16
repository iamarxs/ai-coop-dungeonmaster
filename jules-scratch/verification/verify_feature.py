from playwright.sync_api import Page, expect

def test_create_and_join_game(page: Page):
    # 1. Arrange: Go to the application's homepage.
    page.goto("http://localhost:3000")

    # 2. Act: Create a new game.
    page.get_by_placeholder("Your Name").fill("Host")
    page.get_by_placeholder("Your Class").fill("Warrior")
    page.get_by_placeholder("Scenario").fill("A grand adventure")
    page.get_by_role("button", name="Create Game").click()

    # 3. Assert: Verify the host is in the lobby.
    expect(page.get_by_text("Host (Warrior)")).to_be_visible()

    # 4. Screenshot: Capture the lobby for visual verification.
    page.screenshot(path="jules-scratch/verification/verification.png")
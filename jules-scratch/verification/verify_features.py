import re
from playwright.sync_api import Page, expect

def test_feature_verification(page: Page):
    page.goto("http://localhost:3000")

    # Verify dark mode is on by default
    expect(page.locator("body")).to_have_class(re.compile(r"dark-mode"))
    page.screenshot(path="jules-scratch/verification/01-dark-mode.png")

    # Switch to light mode
    page.get_by_role("button", name="Switch to Light Mode").click()
    expect(page.locator("body")).to_have_class(re.compile(r"light-mode"))
    page.screenshot(path="jules-scratch/verification/02-light-mode.png")

    # Create a game
    page.get_by_placeholder("Scenario").fill("A spooky castle")
    page.get_by_role("button", name="Create Game").click()

    # Join the game
    expect(page.get_by_role("heading", name="Join Game")).to_be_visible()
    page.get_by_placeholder("Your Name").fill("Jules")
    page.get_by_placeholder("Your Class").fill("Wizard")
    page.get_by_role("button", name="Join Game").click()

    # Verify player list
    expect(page.get_by_text("Jules (Wizard)")).to_be_visible()
    page.screenshot(path="jules-scratch/verification/03-player-list.png")
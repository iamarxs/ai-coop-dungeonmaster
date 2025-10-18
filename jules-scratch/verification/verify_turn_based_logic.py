import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context1 = await browser.new_context()
        page = await context1.new_page()

        print("Creating game...")
        await page.goto("http://localhost:3000")
        await page.get_by_placeholder("Your Name").fill("Host")
        await page.get_by_placeholder("Your Class").fill("Warrior")
        await page.get_by_placeholder("Scenario").fill("A classic dungeon crawl")
        await page.get_by_role("button", name="Create Game").click()

        game_id_element = await page.wait_for_selector("h2")
        game_id_text = await game_id_element.inner_text()
        game_id = game_id_text.split(": ")[1]
        print(f"Game created with ID: {game_id}")

        context2 = await browser.new_context()
        page2 = await context2.new_page()
        print("Player 2 joining...")
        await page2.goto("http://localhost:3000")
        await page2.get_by_role("button", name="Join a Game").click()
        await page2.get_by_placeholder("Game ID").fill(game_id)
        await page2.get_by_placeholder("Your Name").fill("Player 2")
        await page2.get_by_placeholder("Your Class").fill("Mage")
        await page2.get_by_role("button", name="Join Game").click()

        print("Starting game...")
        start_game_button = page.get_by_role("button", name="Start Game")
        await start_game_button.click()

        print("Waiting for game to start...")
        await asyncio.sleep(30)

        print("Host's turn...")
        await expect(page.get_by_placeholder("What do you do?")).to_be_enabled(timeout=15000)
        await page.get_by_placeholder("What do you do?").fill("I check for traps.")
        await page.get_by_role("button", name="Send Action").click()
        print("Host's action sent.")

        await asyncio.sleep(3)

        print("Player 2's turn...")
        await expect(page2.get_by_placeholder("What do you do?")).to_be_enabled(timeout=15000)
        await page2.get_by_placeholder("What do you do?").fill("I prepare a magic missile spell.")
        await page2.get_by_role("button", name="Send Action").click()
        print("Player 2's action sent.")

        print("Waiting for AI response...")
        await asyncio.sleep(30)

        print("Taking screenshot...")
        await page.screenshot(path="jules-scratch/verification/turn_based_gameplay.png")
        print("Screenshot taken.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
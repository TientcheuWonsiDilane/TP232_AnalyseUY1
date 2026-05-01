import os
from playwright.async_api import async_playwright
import asyncio

STREAMLIT_URL = os.environ.get("STREAMLIT_URL", "https://tientcheu-wonsi-dilane-24h2589.streamlit.app")

async def wake_app():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Visiting {STREAMLIT_URL}...")
        await page.goto(STREAMLIT_URL, wait_until="domcontentloaded", timeout=120000)
        await page.wait_for_timeout(5000)
        
        # Look for and click the wake-up button
        wake_btn = page.get_by_role("button", name="Yes, get this app back up!")
        if await wake_btn.count() > 0:
            print(f"App was asleep. Clicking wake button...")
            await wake_btn.click()
            await page.wait_for_timeout(60000)  # Wait for app to start
            print("App successfully woken up")
        else:
            print("App was already awake")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(wake_app())

import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup

async def main():
    browser = await uc.start(headless=False)
    page = await browser.get(
        "https://www.x-kom.pl/g-5/c/11-procesory.html")

    for i in range(15):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)

    await asyncio.sleep(5)

    html = await page.get_content()

    # Parsowanie z BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.parts__LinkWithoutAnchorWrapper-sc-f5aee401-0")
    print(f"🔍 Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        try:
            print(item)

        except Exception as e:
            print(f"{i}. ❌ Błąd: {e}")

    await page.close()
    # await browser.close()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())

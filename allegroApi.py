import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup

async def main():
    browser = await uc.start(headless=False)
    page = await browser.get(
        "https://allegro.pl/listing?string=procesor")

    for i in range(15):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)

    await asyncio.sleep(5)

    html = await page.get_content()

    # Parsowanie z BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.mx7m_1")
    print(f"Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        try:
            print(item)
            a_name = item.find("a")
            print(a_name)

        except Exception as e:
            print(f"{i}. Błąd: {e}")

    await page.close()
    # await browser.close()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())

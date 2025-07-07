import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup


async def main():
    browser = await uc.start(headless=False)
    page = await browser.get(
        "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-karta-graficzna/")

    for i in range(15):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)

    await asyncio.sleep(5)

    html = await page.get_content()

    # Parsowanie z BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select('div[class="css-qfzx1y"]')
    print(f"🔍 Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        h3_tag = item.find("h4", class_="css-1g61gc2").getText(strip=True)
        print(h3_tag)

        price_tag = item.select_one('[data-testid="ad-price"]')
        price_value = price_tag.getText(strip=True)
        match = re.search(r"(\d[\d\s]*)\s*zł", price_value)
        print("price: " + match.group(1).replace(" ", ""))

        span_status = soup.find("span", attrs={"title": "Używane"})
        status_value = span_status.getText(strip=True)
        print("status: " + status_value)

        img_div = item.select_one(".css-gl6djm")
        img_tag = img_div.find("img")
        src = img_tag.get("src", "brak src")
        print("src: " + src)

        a_tag = item.select_one(".css-1tqlkj0")
        src = a_tag.get("href", "")
        print("url: " + "https://www.olx.pl/" + src)

        print("*" * 30)


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

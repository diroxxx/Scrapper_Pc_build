import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup


async def main():
    browser = await uc.start(headless=False)
    page = await browser.get(
        "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/karty-graficzne-260019/q/rtx%204070?fromSuggestion=true")

    await asyncio.sleep(5)



    # items = await page.select_all("a.mlc-card.mlc-itembox")

    html = await page.get_content()

    # Parsowanie z BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a.mlc-card.mlc-itembox")
    print(f"🔍 Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        try:
            # h3 = await item.query_selector("h3.mlc-itembox__title")
            title_el = item.find("h3", class_="mlc-itembox__title")
            title = title_el.get_text(strip=True) if title_el else "Brak tytułu"

            price_el = item.select_one(".ml-offer-price__dollars")
            currency_el = item.select_one(".ml-offer-price__currency")
            price = price_el.get_text(strip=True) if price_el else "-"
            currency = currency_el.get_text(strip=True) if currency_el else ""

            loc_el = item.find("address")
            location = loc_el.get_text(strip=True) if loc_el else "Brak lokalizacji"

            href = item.get("href", "")
            url = f"https://allegrolokalnie.pl{href}" if href else "Brak linku"

            img =  item.select_one(".mlc-itembox__image__wrapper img")
            img_src = img.get("src", "Brak src")


            print(f"{i}. 🏷️ {title}")
            print(f"   💰 {price} {currency}")
            print(f"   📍 {location}")
            print(f"   🔗 {url}")
            print(f"🖼️ Obrazek: {img_src}")
            print("-" * 50)

        except Exception as e:
            print(f"{i}. ❌ Błąd: {e}")

    await page.close()
    # await browser.close()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())

import asyncio
import re
import traceback
from time import sleep

from bs4 import BeautifulSoup
import nodriver as uc


async def main():
    url = "https://allegro.pl/oferta/procesory-intel-core-i5-intel-core-i5-14600k-8x3-5-ghz-24-mb-17665847880"
    browser = await uc.start(headless=False)
    page = await browser.get(url)

    for _ in range(4):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    # print(soup.prettify())

    # try:
    #     await asyncio.sleep(5)
    # except Exception as e:
    #     print(f"Error while checking {url}: {e}")
    #     traceback.print_exc()

    # allegro
    # buy_button = soup.find("button", {"id": "add-to-cart-button"}) or \
    #              soup.find("button", {"id": "buy-and-pay-button_SHOW_ITEM_STATIC_DESKTOP"})
    # is_expired = buy_button is None

    is_expired = False

    # allegrolokalne
    # el = soup.find("div", class_="mlc-offer-ended-banner")  # lub soup.select_one("div.mlc-offer-ended-banner")
    # if el:
    #     is_expired = True
    #
    # if not el:
    #     # alternatywnie regex
    #     print("nie ", el)
    #     el = soup.find("div", class_=re.compile(r"mlc-.*ended-banner"))
    #
    # if el:
    #     text = el.get_text(strip=True).lower()
    #     if "ogłoszenie" in text and ("sprzedany" in text or "zakończył" in text):
    #         is_expired = True

    # olx
    # expired = soup.find("h4", string=lambda t: "to ogłoszenie nie jest już dostępne" in t.lower() if t else False)
    # if expired:
    #     is_expired = True


    # allegro

    expired = soup.find("h6", string=lambda t: "sprzedaż zakończona" in t.lower() if t else False)
    if expired:
        is_expired = True

    print("czy jest nieaktywna?: ", is_expired)


if __name__ == "__main__":
    uc.loop().run_until_complete(main())
import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup
from validComponentsApi.extract_details import (
    extract_brand_from_gpu, extract_brand_from_cpu, extract_brand_from_case, extract_brand_from_ssd,
    extract_brand_from_ram, extract_brand_from_power_supply, extract_brand_from_motherboard,
    extract_info_from_gpu
)


CATEGORIES = {
    "processor": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/procesory-257222",
    "graphics_card": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/karty-graficzne-260019",
    "ram": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/pamiec-ram-257226",
    "case": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/obudowy-259436",
    "power_supply": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/zasilacze-259437",
    "motherboard": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/plyty-glowne-4228"
}


async def scrape_category(page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}

    # for i in range(17):
    #     await page.evaluate("window.scrollBy(0, window.innerHeight);")
    #     await asyncio.sleep(1)
    await asyncio.sleep(5)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a.mlc-card.mlc-itembox")
    # print(f"Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        price = 0
        try:
            # h3 = await item.query_selector("h3.mlc-itembox__title")
            title_el = item.find("h3", class_="mlc-itembox__title")
            title = title_el.get_text(strip=True) if title_el else "Brak tytułu"

            price_el = item.select_one(".ml-offer-price__dollars")
            price = price_el.get_text(strip=True) if price_el else 0
            # print(price)/
            href = item.get("href", "")
            url = f"https://allegrolokalnie.pl{href}" if href else "Brak linku"

            img = item.select_one(".mlc-itembox__image__wrapper img")
            img_src = img.get("src", "Brak src")

            comp = {
                "category": category_name,
                # "brand": "",
                # "model": title,
                "price" : float(price.replace(" ", "")),
                "status": "USED",
                "img": img_src,
                "url": url,
                "shop": "allegro_lokalnie"
            }

            if category_name == "graphics_card":
                comp.update(extract_info_from_gpu(title))
            if category_name == "processor":
                comp.update(extract_brand_from_cpu(title))
            if category_name == "case":
                comp.update(extract_brand_from_case(title))
            if category_name == "storage":
                comp.update(extract_brand_from_ssd(title))
            if category_name == "ram":
                comp.update(extract_brand_from_ram(title))
            if category_name == "power_supply":
                comp.update(extract_brand_from_power_supply(title))
            if category_name == "motherboard":
                comp.update(extract_brand_from_motherboard(title))

            all_components[category_name].append(comp)


        except Exception as e:
            print(f"{i}.Błąd: {e}")

    print(f"Znaleziono {len(all_components[category_name])} ofert w kategorii {category_name}.\n")
    return all_components


async def main():
    all_components = []
    browser = await uc.start(headless=True)

    for category_name, url in CATEGORIES.items():
        print(f"Pobieram kategorię: {category_name}")
        page = await browser.get(url)
        items = await scrape_category(page, category_name)
        all_components.extend(items[category_name])

    print(f"Łącznie znaleziono {len(all_components)} ofert.")
    return all_components


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

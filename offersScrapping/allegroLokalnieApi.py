from typing import Any, Dict, List
import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup
from models.dto_models import ComponentOfferDto
from validComponentsApi.extract_details import (
    extract_brand_from_gpu, extract_brand_from_cpu, extract_brand_from_case, extract_brand_from_ssd,
    extract_brand_from_ram, extract_brand_from_power_supply, extract_brand_from_motherboard,
    extract_info_from_gpu
)
from offersScrapping.clean_methods import (is_bundle_offer, clean_title)


CATEGORIES = {
    "processor": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/procesory-257222",
    "graphics_card": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/karty-graficzne-260019",
    "ram": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/pamiec-ram-257226",
    "case": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/obudowy-259436",
    "power_supply": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/zasilacze-259437",
    "motherboard": "https://allegrolokalnie.pl/oferty/podzespoly-komputerowe/plyty-glowne-4228"
}


async def scrape_category(page, category_name: str) -> List[ComponentOfferDto]:
    components = []

    await asyncio.sleep(5)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a.mlc-card.mlc-itembox")

    for i, item in enumerate(cards, start=1):
        try:
            title_el = item.find("h3", class_="mlc-itembox__title")
            title = title_el.get_text(strip=True) if title_el else ""

            price_el = item.select_one(".ml-offer-price__dollars")
            price_text = price_el.get_text(strip=True) if price_el else "0"
            price = safe_parse_price(price_text)

            href = item.get("href", "")
            url = f"https://allegrolokalnie.pl{href}" if href else ""

            img = item.select_one(".mlc-itembox__image__wrapper img")
            img_src = img.get("src", "") if img else ""

            if title:
                if is_bundle_offer(title, category_name):
                    continue
                
                title_cleaned = clean_title(title, category_name)

                extracted_data = {}
                if category_name == "graphics_card":
                    extracted_data = extract_info_from_gpu(title_cleaned)
                elif category_name == "processor":
                    extracted_data = extract_brand_from_cpu(title_cleaned)
                elif category_name == "case":
                    extracted_data = extract_brand_from_case(title_cleaned)
                elif category_name == "storage":
                    extracted_data = extract_brand_from_ssd(title_cleaned)
                elif category_name == "ram":
                    extracted_data = extract_brand_from_ram(title_cleaned)
                elif category_name == "power_supply":
                    extracted_data = extract_brand_from_power_supply(title_cleaned)
                elif category_name == "motherboard":
                    extracted_data = extract_brand_from_motherboard(title_cleaned)

                brand = extracted_data.get("brand")
                model = extracted_data.get("model", title_cleaned)

                component = ComponentOfferDto(
                    title=title,
                    brand=brand,
                    category=category_name,
                    img=img_src,
                    model=model,
                    price=price,
                    shop="allegroLokalnie",
                    status="USED",
                    url=url
                    )
                components.append(component)
                # print(component.title)

        except Exception as e:
            print(f"{i}. Błąd w {category_name}: {e}")

    # print(f"Znaleziono {len(components)} ofert w kategorii {category_name}.\n")
    return components


async def main() -> List[ComponentOfferDto]:
    all_components = []
    browser = await uc.start(headless=True)

    for category_name, url in CATEGORIES.items():
        print(f"Pobieram kategorię: {category_name}")
        page = await browser.get(url)
        items = await scrape_category(page, category_name)
        all_components.extend(items)

    browser.stop()
    print(f"Łącznie znaleziono {len(all_components)} ofert.")
    return all_components    

def safe_parse_price(price_text: str) -> float:
    if not price_text or price_text == 0:
        return 0.0

    price_str = str(price_text)

    price_str = price_str.replace(" ", "").replace("\xa0", "")

    price_str = price_str.replace("zł", "").replace("PLN", "")

    price_str = price_str.replace(",", ".")

    price_str = re.sub(r"[^\d.]", "", price_str)

    try:
        return float(price_str) if price_str else 0.0
    except ValueError:
        return 0.0

if __name__ == "__main__":
    uc.loop().run_until_complete(main())

import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import asyncio
import re
from typing import Any, Dict, List
import nodriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
from models.dto_models import ComponentOfferDto
from validComponentsApi.extract_details import (
    extract_brand_from_case,
    extract_brand_from_power_supply,
    extract_brand_from_motherboard,
    extract_brand_from_ram,
    extract_brand_from_ssd,
    extract_brand_from_cpu,
    extract_info_from_gpu,
)
import re
from offersScrapping.clean_methods import (is_bundle_offer, clean_title)

CATEGORIES = {
    "processor": "https://allegro.pl/kategoria/podzespoly-komputerowe-procesory-257222",
    "graphics_card": "https://allegro.pl/kategoria/podzespoly-komputerowe-karty-graficzne-260019",
    "ram": "https://allegro.pl/kategoria/podzespoly-komputerowe-pamiec-ram-257226",
    "case": "https://allegro.pl/kategoria/podzespoly-komputerowe-obudowy-259436",
    "storage": "https://allegro.pl/kategoria/dyski-i-pamieci-przenosne-dyski-ssd-257335",
    "power_supply": "https://allegro.pl/kategoria/podzespoly-komputerowe-zasilacze-259437",
    "motherboard": "https://allegro.pl/kategoria/podzespoly-komputerowe-plyty-glowne-4228"
}


def _parse_price(text: str) -> float:
    if not text:
        return 0.0
    text = text.replace("\xa0", " ")
    match = re.search(r"(\d+[\s\d]*[,.]?\d*)", text)
    if not match:
        return 0.0
    num = match.group(1).replace(" ", "").replace(",", ".")
    try:
        return float(num)
    except ValueError:
        return 0.0


def _extract_status(item_soup: BeautifulSoup, page_soup: BeautifulSoup) -> str | None:
    status_eng: str | None = None

    stan_dt = item_soup.find("dt", string="Stan")
    if not stan_dt:
        stan_dt = page_soup.find("dt", string="Stan")

    if stan_dt:
        stan_value = stan_dt.find_next_sibling("dd")
        stan_value_text = stan_value.get_text(strip=True).lower() if stan_value else ""
        if stan_value_text == "używany":
            status_eng = "USED"
        elif stan_value_text == "nowy":
            status_eng = "NEW"
        else:
            status_eng = "DEFECTIVE"

    return status_eng


async def scrape_category(page, category_name: str) -> List[ComponentOfferDto]:
    components = []

    for _ in range(30):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)
    await asyncio.sleep(5)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article")

    for i, item in enumerate(cards, start=1):
        try:
            # Image
            photo_link = item.find("a")
            photo_img = photo_link.find("img") if photo_link else None
            photo_url = photo_img.get("src", "") if photo_img else ""

            title_element = item.find("h2")
            title_link = title_element.find("a") if title_element else None
            title = title_link.get_text(strip=True) if title_link else ""
            website_url_raw = title_link.get("href", "") if title_link else ""
            website_url = clean_allegro_url(website_url_raw)

            price: float = 0.0
            price_element = item.find(
                "span",
                class_=lambda x: x and "mli8_k4" in x and "msa3_z4" in x and "mqu1_1" in x,
            )
            if not price_element:
                price_element = item.find("span", attrs={"aria-label": lambda x: bool(x and "zł" in x)})
            if price_element:
                price = _parse_price(price_element.get_text(strip=True))

            status_eng = _extract_status(item, soup)
            if status_eng == "DEFECTIVE":
                continue

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
                    img=photo_url,
                    model=model,
                    price=price,
                    shop="allegro",
                    status=status_eng,
                    url=website_url
                    )
                components.append(component)
                # print(component.title)

        except Exception as e:
            print(f"{i}. Błąd w {category_name}: {e}")

    # print(f"Znaleziono {len(components)} ofert w kategorii {category_name}.\n")
    return components 

async def main() -> List[ComponentOfferDto]:
    all_components = []
    browser = await uc.start(headless=False)

    for category_name, url in CATEGORIES.items():
        print(f"Pobieram kategorię: {category_name}")
        page = await browser.get(url)
        await asyncio.sleep(2)
        items = await scrape_category(page, category_name)
        all_components.extend(items)

    browser.stop()
    print(f"Łącznie znaleziono {len(all_components)} ofert.")
    return all_components


def clean_allegro_url(url):
    if not url or url == "Brak linku do strony":
        return url

    if "/events/clicks" in url:
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            if 'redirect' in params:
                redirect_url = unquote(params['redirect'][0])
                clean_url = redirect_url.split('?')[0]
                return clean_url
        except Exception:
            pass

    return url.split('?')[0]

if __name__ == "__main__":
    uc.loop().run_until_complete(main())

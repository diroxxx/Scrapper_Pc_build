import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup

from models.dto_models import ComponentOfferDto
from validComponentsApi.extract_details import (
    extract_brand_from_gpu, extract_brand_from_cpu, extract_brand_from_case, extract_brand_from_ssd,
    extract_brand_from_ram, extract_brand_from_power_supply, extract_brand_from_motherboard,
    extract_info_from_gpu )

from offersScrapping.clean_methods import (is_bundle_offer, clean_title)

CATEGORIES = {
    "processor": "https://www.x-kom.pl/g-5/c/11-procesory.html",
    "graphics_card": "https://www.x-kom.pl/g-5/c/345-karty-graficzne.html",
    "ram": "https://www.x-kom.pl/g-5/c/28-pamieci-ram.html",
    "case": "https://www.x-kom.pl/g-5/c/388-obudowy-komputerowe.html",
    "storage" : "https://www.x-kom.pl/g-5/c/1779-dyski-ssd.html",
    "power_supply" : "https://www.x-kom.pl/g-5/c/158-zasilacze-do-komputera.html",
    "motherboard" : "https://www.x-kom.pl/g-5/c/14-plyty-glowne.html"
}


async def scrape_category(page, category_name):
    components = []

    for _ in range(11):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)
    await asyncio.sleep(3)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all(attrs={"data-name": "productCard"})
    for item in cards:
        try:
            h3 = item.find('h3', {'title': True})
            title = h3.get('title')
            print(title)

            price_div = soup.find('div', {'data-name': 'productPrice'})
            price = 0.0
            spans = price_div.find_all('span')
            if spans:
                price_text = spans[0].get_text(strip=True)
                price = float(price_text.replace("Cena:", "").replace(",", ".").replace("zł", "").replace(" ", ""))
                # print("cena po zamianie:", price)

            img_tag = item.select_one("img")
            img_src = str(img_tag.get("src", "")) if img_tag else ""
            # print(img_src)
            #
            link_tag = item.select_one("a")
            url = "https://www.x-kom.pl" + str(link_tag.get("href", "")) if link_tag else ""
            # print(url)


            if title:
                if is_bundle_offer(title, category_name):
                    # print(f"Pominięto zestaw: {title}")
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
                        price= price,
                        shop="x-kom",
                        status="NEW",
                        url=url
                        )
                components.append(component)

        except Exception as e:
            print(f"Błąd w {category_name}: {e}")

    return components


async def main():
    all_components = []
    browser = await uc.start(headless=True)

    for category_name, url in CATEGORIES.items():
        page = await browser.get(url)
        items = await scrape_category(page, category_name)
        all_components.extend(items)

    browser.stop()
    return all_components


if __name__ == "__main__":
    uc.loop().run_until_complete(main())


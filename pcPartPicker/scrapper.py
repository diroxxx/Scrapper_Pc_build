import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup
from validComponentsApi.extract_details import (
    extract_brand_from_case,
    extract_brand_from_power_supply,
    extract_brand_from_motherboard,
    extract_brand_from_cpu_cooler,
    extract_brand_from_ram,
    extract_brand_from_ssd,
    extract_brand_from_cpu,
    extract_brand_from_gpu,
    extract_info_from_gpu
)

CATEGORIES = {
    "processor": "https://pcpartpicker.com/products/cpu/",
    "graphics_card": "https://pcpartpicker.com/products/video-card/",
    "ram": "https://pcpartpicker.com/products/memory/",
    "case": "https://pcpartpicker.com/products/case/",
    "storage": "https://pcpartpicker.com/products/internal-hard-drive/",
    "power_supply": "https://pcpartpicker.com/products/power-supply/",
    "motherboard": "https://pcpartpicker.com/products/motherboard/",
    "cpu_cooler": "https://pcpartpicker.com/products/cpu-cooler/"

}


async def scrape_category(page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}

    for i in range(10):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)
    await asyncio.sleep(2)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("tr")
    print(f"Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        try:
            # link = item.select_one("a")
            a = item.select_one("a").attrs["href"]
            link = "https://pcpartpicker.com" + a
            print(link)
            browser = await uc.start(headless=False)
            page2 = await browser.get(link)
            html2 = await page2.get_content()
            soup2 = BeautifulSoup(html2, "html.parser")
            info = soup2.find('a', href=True)
            print(info)
            print("\n")


        except Exception as e:
            print(f"{i}. Błąd: {e}")

    print(f"Znaleziono {len(all_components[category_name])} ofert w kategorii {category_name}.\n")
    return all_components


async def main():
    all_components = []
    browser = await uc.start(headless=False)

    for category_name, url in CATEGORIES.items():
        print(f"Pobieram kategorię: {category_name}")
        page = await browser.get(url)
        await asyncio.sleep(3)
        items = await scrape_category(page, category_name)
        all_components.extend(items[category_name])

    browser.stop()
    print(len(all_components))
    return all_components


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

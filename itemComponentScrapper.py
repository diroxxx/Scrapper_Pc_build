import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup
from validComponentsApi.extract_details import (
    extract_brand_from_cpu,
    extract_info_from_gpu,
    extract_brand_from_case,
    extract_brand_from_power_supply,
    extract_brand_from_motherboard,
    extract_brand_from_cpu_cooler,
    extract_brand_from_ram,
    extract_brand_from_ssd,

)

CATEGORIES = {
    "processor": "https://www.pc-kombo.com/ca/components/cpus",
    "graphics_card": "https://www.pc-kombo.com/ca/components/gpus",
    "ram": "https://www.pc-kombo.com/ca/components/rams",
    "case": "https://www.pc-kombo.com/ca/components/cases",
    "ssd": "https://www.pc-kombo.com/ca/components/ssds",
    "power_supply": "https://www.pc-kombo.com/ca/components/psus",
    "motherboard": "https://www.pc-kombo.com/ca/components/motherboards",
    "cpu_cooler": "https://www.pc-kombo.com/ca/components/cpucoolers"
}
media_types = ["nvme", "sata", "ssd", "solid state drive", "hdd", "m.2"]


async def scrape_category(page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("li.columns")

    print(f"Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        try:
            comp = {}
            title = item.find("h5").text
            # print(title)
            title = title.lower()
            if category_name == "processor":
                # comp["brand"] = extract_brand_from_cpu(title)

                comp["socket"] = item.select_one("span.socket").text
                comp["cores"] = item.select_one("span.cores").text
                tmp = extract_brand_from_cpu(title)
                comp["brand"] = tmp["brand"]
                comp["model"] = tmp["model"]
                # comp["threads"] = item.select_one("span.threads").text

            if category_name == "graphics_card":
                comp["brand"] = extract_info_from_gpu(title)
                comp["model"] =  re.sub(r"\s*\([^)]*\)", "", item.select_one("span.series").text).strip()
                comp["vram"] = item.select_one("span.vram").text
                comp["gddr"] = None
                comp["power_draw"] = None

            if category_name == "case":
                # comp["brand"] = extract_brand_from_case(title)
                comp["format"] = item.select_one("span.size").text.lower()
                tmp = extract_brand_from_cpu(title)
                comp["brand"] = tmp["brand"]
                comp["model"] = tmp["model"]
            if category_name == "ssd":
                comp.update(extract_brand_from_ssd(title))
                comp["capacity"] = item.select_one("span.size").text

            if category_name == "ram":
                comp.update(extract_brand_from_ram(title))
                comp["capacity"] = item.select_one("span.size").text
                tmp = item.select_one("span.type").text
                if "-" in tmp:
                    type_part, speed_part = tmp.strip().upper().split("-")
                    comp["type"]: type_part
                    comp["speed"]: speed_part
                comp["latency"] = None

            if category_name == "power_supply":
                comp.update(extract_brand_from_power_supply(title))
                comp["maxPowerWatt"] = item.select_one("span.watt").text

            if category_name == "motherboard":
                comp.update(extract_brand_from_motherboard(title))
                comp["socket"] = item.select_one("span.socket").text
                comp["format"] = item.select_one("span.size").text
                comp["chipset"] = item.select_one("span.chipset").text

            if category_name == "cpu_cooler":
                comp.update(extract_brand_from_cpu_cooler(title))

                tmp = item.select_one("span.sockets").text
                pattern = r"\b(?:\d{3,4}(?:-v\d)?|am\d\+?|fm\d\+?)\b"
                sockets = re.findall(pattern, tmp.lower())
                comp["socket"] = sockets

            # print(comp)
            # print("\n")
            all_components[category_name].append(comp)

        except Exception as e:
            print(f"{i}. Błąd: {e}")

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

    browser.stop()
    # print(len(all_components))
    return all_components


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

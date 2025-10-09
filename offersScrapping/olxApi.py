import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup
from validComponentsApi.extract_details import (
    extract_brand_from_gpu, extract_brand_from_cpu, extract_brand_from_case, extract_brand_from_ssd,
    extract_brand_from_ram, extract_brand_from_power_supply, extract_brand_from_motherboard,
    extract_info_from_gpu
)

GPU_BRANDS = {
    "asus", "msi", "gigabyte", "zotac", "evga", "palit", "gainward", "xfx", "powercolor", "sapphire", "inno3d", "nvidia"
}

CATEGORIES = {
    "processor": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/procesory/q-procesor/",
    "graphics card": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-karta-graficzna/",
    "ram": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-ram/",
    "case": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-obudowa/",
    "storage": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-ssd/",
    "power_supply": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-zasilacz/",
    "motherboard": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-płyta-główna/"
}


async def scrape_category(page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}

    for _ in range(20):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)
    await asyncio.sleep(3)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select('[data-cy="l-card"]')

    for item in cards:
        try:
            title_tag = item.find("h4", class_="css-hzlye5")
            title = title_tag.getText(strip=True) if title_tag else ""

            price_tag = item.select_one('[data-testid="ad-price"]')
            price_text = price_tag.getText(strip=True) if price_tag else ""
            price_match = re.search(r"(\d[\d\s]*)\s*zł", price_text)
            price = price_match.group(1).replace(" ", "") if price_match else 0



            img_tag = item.select_one("img")
            img_src = str(img_tag.get("src", "")) if img_tag else ""

            link_tag = item.select_one("a.css-1tqlkj0")
            url = "https://www.olx.pl" + str(link_tag.get("href", "")) if link_tag else ""


            status_span = item.find("span", attrs={"title": "Używane"})
            status = status_span.getText(strip=True) if status_span else "Nieznany"
            print(status)
            status_eng = None
            if status.lower() == "używane":
                status_eng = "USED"
            elif status.lower() == "nowe":
                status_eng = "NEW"
            else:
                status_eng = "DEFECTIVE"

            if title:
                if is_bundle_offer(title, category_name):
                    print(f"Pominięto zestaw: {title}")
                    continue
                title = clean_title(title, category_name)

                extracted_data = {}
                if category_name == "graphics_card":
                    extracted_data = extract_info_from_gpu(title)
                elif category_name == "processor":
                    extracted_data = extract_brand_from_cpu(title)
                elif category_name == "case":
                    extracted_data = extract_brand_from_case(title)
                elif category_name == "storage":
                    extracted_data = extract_brand_from_ssd(title)
                elif category_name == "ram":
                    extracted_data = extract_brand_from_ram(title)
                elif category_name == "power_supply":
                    extracted_data = extract_brand_from_power_supply(title)
                elif category_name == "motherboard":
                    extracted_data = extract_brand_from_motherboard(title)

                comp = {
                    "category": category_name,
                    "brand": extracted_data.get("brand"),
                    "model": extracted_data.get("model", title),
                    "price": float(price),
                    "status": status_eng,
                    "img": img_src,
                    "url": url,
                    "shop": "olx"
                }

                if comp["brand"] is not None and comp["model"] is not None:
                    # print(f"Adding component: {comp}")
                    # print("\n")
                    all_components[category_name].append(comp)

        except Exception as e:
            print(f"Błąd w {category_name}: {e}")

    print(f"Znaleziono {len(all_components[category_name])} ofert w kategorii {category_name}.\n")
    return all_components



def clean_title(title: str, category: str) -> str:
    if not title:
        return title

    keywords_to_remove = {
        "processor": [
            r"\bprocesor\b",
            r"\bCPU\b",
            r"\bBox\b",
            r"\bOEM\b",
            r"\bTray\b",
        ],
        "graphics_card": [
            r"\bkarta graficzna\b",
            r"\bgraphics card\b",
            r"\bGPU\b",
            r"\bVGA\b",
        ],
        "ram": [
            r"\bpamięć\b",
            r"\bpamiec\b",
            r"\bRAM\b",
            r"\bmemory\b",
        ],
        "case": [
            r"\bobudowa\b",
            r"\bcase\b",
            r"\bshell\b",
        ],
        "storage": [
            r"\bdysk\b",
            r"\bSSD\b",
            r"\bHDD\b",
            r"\bNVMe\b",
            r"\bSATA\b",
        ],
        "power_supply": [
            r"\bzasilacz\b",
            r"\bPSU\b",
            r"\bpower supply\b",
        ],
        "motherboard": [
            r"\bpłyta główna\b",
            r"\bplyta glowna\b",
            r"\bmotherboard\b",
            r"\bmobo\b",
        ],
    }

    general_keywords = [
        r"\bnowy\b",
        r"\bnowa\b",
        r"\bnowe\b",
        r"\bużywany\b",
        r"\buzywany\b",
        r"\bużywana\b",
        r"\bfv\b",
        r"\bgwarancja\b",
        r"\bpolecam\b",
        r"\btanio\b",
        r"\bokazja\b",
        r"\bsprzedam\b",
    ]

    cleaned = title

    if category in keywords_to_remove:
        for keyword in keywords_to_remove[category]:
            cleaned = re.sub(keyword, "", cleaned, flags=re.IGNORECASE)

    for keyword in general_keywords:
        cleaned = re.sub(keyword, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s*[-,/|]\s*', ' ', cleaned)
    cleaned = cleaned.strip(' -,/|')

    return cleaned


def is_bundle_offer(title: str,category: str = None) -> bool:
    if not title:
        return False

    bundle_keywords = [
        r'\bzestaw\b',
        r'\bset\b',
        r'\bkomplet\b',
        r'\bbundle\b',
        r'\bpc\s+gaming\b',
        r'\bkomputer\b',
        r'\bzestaw do gier\b',
        r'\bzestaw komputerowy\b',
    ]

    for keyword in bundle_keywords:
        if re.search(keyword, title, flags=re.IGNORECASE):
            return True

    component_keywords = [
        r'\bprocesor\b',
        r'\bcpu\b',
        r'\bkarta graficzna\b',
        r'\bgpu\b',
        r'\bgtx\b',
        r'\brtx\b',
        r'\bpłyta\s+główna\b',
        r'\bplyta\s+glowna\b',
        r'\bmotherboard\b',
        r'\bmobo\b',
        r'\bzasilacz\b',
        r'\bpsu\b',
        r'\bobudowa\b',
        r'\bcase\b',
        r'\bdysk\b',
        r'\bssd\b',
        r'\bhdd\b',
    ]
    if category != "ram":
        component_keywords.extend([
            r'\bpamięć\b',
            r'\bpamiec\b',
            r'\bram\b',
            r'\bddr\d\b',
        ])

    component_count = sum(1 for keyword in component_keywords
                          if re.search(keyword, title, flags=re.IGNORECASE))

    if component_count >= 3:
        return True

    plus_pattern = r'\b(procesor|cpu|gpu|ram|płyta|plyta|dysk|zasilacz|obudowa)\s*\+\s*(procesor|cpu|gpu|ram|płyta|plyta|dysk|zasilacz|obudowa)\b'
    if re.search(plus_pattern, title, flags=re.IGNORECASE):
        return True

    return False

async def main():
    all_components = []
    browser = await uc.start(headless=True)

    for category_name, url in CATEGORIES.items():
        print(f"Pobieram kategorię: {category_name}")
        page = await browser.get(url)
        items = await scrape_category(page, category_name)
        all_components.extend(items[category_name])

    print(len(all_components))
    return all_components


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

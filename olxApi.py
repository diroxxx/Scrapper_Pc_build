import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup
from validComponentsApi.extract_details import extract_cpu_details, extract_gpu_details

GPU_BRANDS = {
    "asus", "msi", "gigabyte", "zotac", "evga", "palit", "gainward", "xfx", "powercolor", "sapphire", "inno3d", "nvidia"
}

CATEGORIES = {
    "processor": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/procesory/q-procesor/",
    "graphics card": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-karta-graficzna/",
    "ram": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-ram/",
    "case": "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-obudowa/",
    "storage" : "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-ssd/",
    "power_Supply" : "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-zasilacz/",
    "motherboard" : "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-płyta-główna/"
}


async def scrape_category(page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}

    for _ in range(20):  # scroll down kilka razy
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)
    await asyncio.sleep(3)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select('[data-cy="l-card"]')

    for item in cards:
        try:
            title = item.find("h4", class_="css-1g61gc2").getText(strip=True)

            price_tag = item.select_one('[data-testid="ad-price"]')
            price_text = price_tag.getText(strip=True)
            price_match = re.search(r"(\d[\d\s]*)\s*zł", price_text)
            price = price_match.group(1).replace(" ", "") if price_match else "Brak ceny"

            status_span = item.find("span", attrs={"title": "Używane"})
            status = status_span.getText(strip=True) if status_span else "Nieznany"

            img_tag = item.select_one("img")
            img_src = str(img_tag.get("src", "")) if img_tag else ""

            link_tag = item.select_one("a.css-1tqlkj0")
            url = "https://www.olx.pl" + str(link_tag.get("href", "")) if link_tag else ""
            comp = {
                        "category": category_name,
                        "name": title,
                        # "brand": for brand in
                        "price": price,
                        "status": status,
                        "img": img_src,
                        "url": url
                        }
            
            if category_name == "graphics_card":
                comp.append(extract_gpu_details(title))
            if category_name == "processor":
                comp.append(extract_cpu_info(title))
            
            
            # elif category_name == "processor":
            #     comp = extract_cpu_details(title)
            # else :
            #     pass
                 
            all_components[category_name].append(comp)



        except Exception as e:
            print(f"Błąd w {category_name}: {e}")

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

    print(len(all_components))
    return all_components


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup
from validComponentsApi.extract_details import (
    extract_gpu_details,
    extract_cpu_info,
    extract_case_info,
    extract_ram_info,
    extract_storage_info,
    extract_motherboard_info,
    extract_power_supply_info)

CATEGORIES = {
    "processor": "https://allegro.pl/kategoria/podzespoly-komputerowe-procesory-257222",
    "graphics_card": "https://allegro.pl/kategoria/podzespoly-komputerowe-karty-graficzne-260019",
    "ram": "https://allegro.pl/kategoria/podzespoly-komputerowe-pamiec-ram-257226",
    "case": "https://allegro.pl/kategoria/podzespoly-komputerowe-obudowy-259436",
    "storage": "https://allegro.pl/kategoria/dyski-i-pamieci-przenosne-dyski-ssd-257335",
    "power_supply": "https://allegro.pl/kategoria/podzespoly-komputerowe-zasilacze-259437",
    "motherboard": "https://allegro.pl/kategoria/podzespoly-komputerowe-plyty-glowne-4228"

}


async def scrape_category(page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}

    for i in range(17):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)
    await asyncio.sleep(5)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article")
    # print(soup)
    # print(f"Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        try:
            photo = item.find("a")
            photo_url = photo.find("img")
            photo_url = photo_url["src"] if photo_url else "Brak zdjęcia"
            # print("photo: ", photo_url)

            title_element = item.find("h2")
            title = title_element.text.strip() if title_element else "Brak tytułu"

            website_url_a = item.find("a")
            website_url = website_url_a["href"] if website_url_a else "Brak linku do strony"

            price_element = item.find("span", class_="mli8_k4 msa3_z4 mqu1_1 mp0t_ji m9qz_yo mgn2_27 mgn2_30_s mgmw_g5")
            if price_element:
                price_text = price_element.get_text(strip=True)
                # print(f"Pełny tekst: '{price_text}'")  # Powinno dać: "383,99 zł"

                # Wyciągnij samą cenę
                price_match = re.search(r'(\d+[,.]?\d*)', price_text)
                price = price_match.group(1) if price_match else "Brak ceny"
                print(f"Cena: '{price}'")  # Powinno dać: "383,99"

            stan_label = item.find("span", string="Stan")
            status = stan_label.find_next_sibling("span") if stan_label else None
            status_text = status.text.strip() if status else "Brak statusu"
            # print("status: ", status_text)

            status_eng = None
            if status_text.lower() == "Używany":
                status_eng = "USED"
            elif status_text.lower() == "Nowy":
                status_eng = "NEW"
            else:
                status_eng = "DEFECTIVE"

            comp = {
                "category": category_name,
                "brand": "",
                "model": title,
                "price": price,
                "status": status_eng,
                "img": photo_url,
                "url": website_url,
                "shop": "allegro"
            }

            if category_name == "graphics_card":
                comp.update(extract_gpu_details(title))
            if category_name == "processor":
                comp.update(extract_cpu_info(title))
            if category_name == "case":
                comp.update(extract_case_info(title))
            if category_name == "storage":
                comp.update(extract_storage_info(title))
            if category_name == "ram":
                comp.update(extract_ram_info(title))
            if category_name == "power_supply":
                comp.update(extract_power_supply_info(title))
            if category_name == "motherboard":
                comp.update(extract_motherboard_info(title))

            # print(comp)
            # print("\n")
            all_components[category_name].append(comp)



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
        await asyncio.sleep(2)
        items = await scrape_category(page, category_name)
        all_components.extend(items[category_name])

    browser.stop()
    print(len(all_components))
    return all_components


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

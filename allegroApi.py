import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
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

    for i in range(23):
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
            # Pobieranie zdjęcia
            photo_link = item.find("a")
            photo_img = photo_link.find("img") if photo_link else None
            photo_url = photo_img["src"] if photo_img else "Brak zdjęcia"

            # Pobieranie tytułu z linka w h2
            title_element = item.find("h2")
            title_link = title_element.find("a") if title_element else None
            title = title_link.text.strip() if title_link else "Brak tytułu"

            # Pobieranie URL produktu z linka w h2
            website_url_raw = title_link["href"] if title_link else "Brak linku do strony"
            website_url = clean_allegro_url(website_url_raw)
            print(f"{i}. Tytuł: {title}")
            print(f"URL: {website_url}")

            # Pobieranie ceny - używamy bardziej ogólnego selektora
            price = 0
            # Szukamy spana z ceną - może mieć różne klasy
            price_element = item.find("span", class_=lambda x: x and "mli8_k4" in x and "msa3_z4" in x and "mqu1_1" in x)
            if not price_element:
                # Alternatywny sposób - szukanie przez aria-label
                price_element = item.find("span", attrs={"aria-label": lambda x: x and "zł" in x if x else False})
            
            if price_element:
                price_text = price_element.get_text(strip=True)
                print(f"Pełny tekst ceny: '{price_text}'")

                # Wyciągnij cenę (liczbę przed "zł")
                price_match = re.search(r'(\d+[,.]?\d*)', price_text.replace('\xa0', ' '))
                if price_match:
                    price = price_match.group(1).replace(",", ".")
                    price = float(price)
                    print(f"Cena: {price}")
            else:
                print("Nie znaleziono elementu z ceną")

            # Pobieranie statusu produktu
            stan_span = item.find("span", string="Stan")
            status = stan_span.find_next_sibling("span") if stan_span else None
            status_text = status.text.strip() if status else "Brak statusu"
            print("status: ", status_text)

            status_eng = None
            if status_text.lower() == "Używany":
                status_eng = "USED"
            elif status_text.lower() == "Nowy":
                status_eng = "NEW"
            else:
                status_eng = "DEFECTIVE"

            if title:

                comp = {
                    "category": category_name,
                    # "brand": "",
                    "model": title,
                    "price" : price,
                    "status": status_eng,
                    "img": photo_url,
                    "url": website_url,
                    "shop": "allegro"
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

def clean_allegro_url(url):
    """Wyciąga czysty URL produktu z linku trackingowego Allegro"""
    if not url or url == "Brak linku do strony":
        return url
    
    # Jeśli to link trackingowy (/events/clicks)
    if "/events/clicks" in url:
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # Szukamy parametru 'redirect' który zawiera prawdziwy URL
            if 'redirect' in params:
                redirect_url = unquote(params['redirect'][0])
                # Usuwamy dodatkowe parametry bi_s, bi_m, etc.
                clean_url = redirect_url.split('?')[0]
                return clean_url
        except:
            pass
    
    # Jeśli to już czysty link lub nie udało się wyczyścić
    return url.split('?')[0]  # Usuń parametry query

if __name__ == "__main__":
    uc.loop().run_until_complete(main())

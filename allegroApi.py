
import asyncio
import nodriver as uc
import re
from bs4 import BeautifulSoup

CATEGORIES = {
    "procesor": "https://allegro.pl/kategoria/podzespoly-komputerowe-procesory-257222",
    # "procesor": "https://allegro.pl/listing?string=procesor"
    "karta graficzna": "https://allegro.pl/kategoria/podzespoly-komputerowe-karty-graficzne-260019",
    "ram": "https://allegro.pl/kategoria/podzespoly-komputerowe-pamiec-ram-257226",
    "case": "https://allegro.pl/kategoria/podzespoly-komputerowe-obudowy-259436",
    "storage": "https://allegro.pl/kategoria/dyski-i-pamieci-przenosne-dyski-ssd-257335",
    "power_Supply": "https://allegro.pl/kategoria/podzespoly-komputerowe-zasilacze-259437",
    "motherboard": "https://allegro.pl/kategoria/podzespoly-komputerowe-plyty-glowne-4228"

}

async def scrape_category(page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}

    # browser = await uc.start(headless=False)
    # page = await browser.get(
    #     "https://allegro.pl/listing?string=procesor")

    for i in range(17):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(1)
    await asyncio.sleep(5)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article")

    print(f"Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        try:
            # print(item)
            photo = item.find("a")
            photo_url = photo.find("img")
            photo_url = photo_url["src"] if photo_url else "Brak zdjęcia"
            # print("photo: ", photo_url)

            title_element = item.find("h2")
            title = title_element.text.strip() if title_element else "Brak tytułu"
            # print("title: ", title)

            website_url_a = item.find("a")
            website_url = website_url_a["href"] if website_url_a else "Brak linku do strony"

            # print("website_url: ", website_url)

            price_element = item.find("span", attrs={"aria-label": True})
            price = price_element["aria-label"] if price_element else "Brak ceny"

            stan_label = item.find("span", string="Stan")
            status = stan_label.find_next_sibling("span") if stan_label else None
            status_text = status.text.strip() if status else "Brak statusu"
            # print("price: ", price)

            # print("---\n")

            all_components[category_name].append({
                "category": category_name,
                "name": title,
                "price": price,
                "status": status_text,
                "img": photo_url,
                "url": website_url
            })
            if(category_name == "procesor"):
                print(f"{i}. {title} - {price} - {status_text} - {photo_url} - {website_url}")
                print("---\n")
        
    
        except Exception as e:
            print(f"{i}. Błąd: {e}")

    print(f"Znaleziono {len(all_components[category_name])} ofert w kategorii {category_name}.\n")
    # await page.close()
    # print(all_components[category_name])
    return all_components

    # await browser.close()




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

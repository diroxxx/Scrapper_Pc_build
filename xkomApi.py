import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

GPU_BRANDS = {
    "asus", "msi", "gigabyte", "zotac", "evga", "palit", "gainward", "xfx", "powercolor", "sapphire", "inno3d", "nvidia"
}

CATEGORIES = {
    "procesor": "https://www.x-kom.pl/g-5/c/11-procesory.html"
    # "karta graficzna": "https://www.x-kom.pl/g-5/c/345-karty-graficzne.html",
    # "ram": "https://www.x-kom.pl/g-5/c/28-pamieci-ram.html",
    # "case": "https://www.x-kom.pl/g-5/c/388-obudowy-komputerowe.html",
    # "storage" : "https://www.x-kom.pl/g-5/c/1779-dyski-ssd.html",
    # "power_Supply" : "https://www.x-kom.pl/g-5/c/158-zasilacze-do-komputera.html",
    # "motherboard" : "https://www.x-kom.pl/g-5/c/14-plyty-glowne.html"
}


# async def scrape_category(page, category_name):
#     all_components = {cat: [] for cat in CATEGORIES}

#     for _ in range(10):  # scroll down kilka razy
#         await page.evaluate("window.scrollBy(0, window.innerHeight);")
#         await asyncio.sleep(1)
#     await asyncio.sleep(2)

#     html = await page.get_content()
#     soup = BeautifulSoup(html, "html.parser")
#     cards = soup.select('div[class*="parts__ProductCardWrapper-sc-e75c88c8-3 MzImC"]')    
#     print(html)
    # for item in cards:
    #     try:
    #         print(item)




            # all_components[category_name].append({
            #     "category": category_name,
            #     "name": title,
            #     "price": price,
            #     "status": status,
            #     "img": img_src,
            #     "url": url
            # })

        # except Exception as e:
        #     print(f"Błąd w {category_name}: {e}")

    # print(f"Znaleziono {len(all_components[category_name])} ofert w kategorii {category_name}.\n")
    # return all_components


# async def main():
#     all_components = []
#     browser = await uc.start(headless=False)

#     for category_name, url in CATEGORIES.items():
#         print(f"Pobieram kategorię: {category_name}")
#         page = await browser.get(url)
#         items = await scrape_category(page, category_name)
#         # all_components.extend(items[category_name])

#     # print(len(all_components))
#     return all_components


# if __name__ == "__main__":
#     uc.loop().run_until_complete(main())


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.x-kom.pl/g-5/c/11-procesory.html")
        await page.wait_for_selector('a.parts__ProductImageLink-sc-a190980b-19', timeout=30000)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select('a.parts__ProductImageLink-sc-a190980b-19')
        print(f"Znaleziono {len(cards)} produktów")
        await browser.close()

asyncio.run(main())
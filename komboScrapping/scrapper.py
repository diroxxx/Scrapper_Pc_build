import asyncio
import re
from bs4 import BeautifulSoup
import nodriver as uc
import sys
import os
import csv

# Add parent directory to Python path to find validComponentsApi
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from validComponentsApi.extract_details import (
    extract_brand_from_cpu,
    extract_brand_from_gpu,
    extract_brand_from_case,
    extract_brand_from_power_supply,
    extract_brand_from_motherboard,
    extract_brand_from_cpu_cooler,
    extract_brand_from_ram,
    extract_brand_from_ssd
)

CATEGORIES = {
    "processor": "https://www.pc-kombo.com/ca/components/cpus",
    "graphics_card": "https://www.pc-kombo.com/ca/components/gpus",
    "ram": "https://www.pc-kombo.com/ca/components/rams",
    "case": "https://www.pc-kombo.com/ca/components/cases",
    "ssd": "https://www.pc-kombo.com/ca/components/ssds",
    "power_supply": "https://www.pc-kombo.com/ca/components/psus",
    "cpu_cooler": "https://www.pc-kombo.com/ca/components/cpucoolers",
    "motherboard": "https://www.pc-kombo.com/ca/components/motherboards"
}
media_types = ["nvme", "sata", "ssd", "solid state drive", "hdd", "m.2"]


async def scrape_category(page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}
    await asyncio.sleep(5)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("li.columns")

    print(f"Znaleziono {len(cards)} ofert:\n")

    for i, item in enumerate(cards, start=1):
        try:
            comp = {}
            title = item.find("h5").text
            print("title: ", title)
            title = title.lower()
            if category_name == "processor":
                tmp = extract_brand_from_cpu(title)
                comp["brand"] = tmp["brand"]
                comp["model"] = tmp["model"]
                comp["socket"] = item.select_one("span.socket").text
                comp["cores"] = item.select_one("span.cores").text

                # Extract threads and base clock from spans without class
                subtitle_div = item.select_one("div.subtitle")
                threads = None
                base_clock = None
                if subtitle_div:
                    spans = subtitle_div.find_all("span")
                    for span in spans:
                        if span.get("class") is None:
                            if "Threads" in span.text:
                                threads_match = re.search(r'(\d+)\s*Threads', span.text)
                                if threads_match:
                                    threads = threads_match.group(1)
                            elif "Clock" in span.text and "GHz" in span.text:
                                clock_match = re.search(r'Clock\s+([\d.]+)\s*GHz', span.text)
                                if clock_match:
                                    base_clock = float(clock_match.group(1))
                comp["threads"] = threads
                comp["base_clock"] = base_clock
                # print(f"Processor: {comp}")

            if category_name == "graphics_card":
                # print(title)
                comp["brand"] = extract_brand_from_gpu(title)
                comp["model"] = re.sub(r"\s*\([^)]*\)", "", item.select_one("span.series").text).strip()
                comp["vram"] = item.select_one("span.vram").text
                comp["gddr"] = None

                # Extract power draw from span without class
                subtitle_div = item.select_one("div.subtitle")
                power_draw = None
                if subtitle_div:
                    spans = subtitle_div.find_all("span")
                    for span in spans:
                        if span.get("class") is None and "W" in span.text:
                            power_match = re.search(r'(\d+)W', span.text)
                            if power_match:
                                power_draw = int(power_match.group(1))
                            break
                comp["power_draw"] = power_draw

                # print(f"Graphics Card: {comp}")

            if category_name == "case":
                comp["format"] = item.select_one("span.size").text.lower()
                comp.update(extract_brand_from_case(title))
                # print(f"Case: {comp}")

            if category_name == "ssd":
                comp.update(extract_brand_from_ssd(title))

                # Remove GB and convert to float
                capacity_text = item.select_one("span.size").text
                capacity_clean = re.sub(r'\s*gb\s*', '', capacity_text, flags=re.IGNORECASE).strip()
                comp["capacity"] = float(capacity_clean)
                # print(f"SSD: {comp}")

            if category_name == "ram":
                comp.update(extract_brand_from_ram(title))
                size_text = item.select_one("span.size").text
                clean_capacity = re.sub(r"\s*gb\s*", "", size_text, flags=re.IGNORECASE)
                comp["capacity"] = int(clean_capacity)
                tmp = item.select_one("span.type").text
                # do poprawy
                if "-" in tmp:
                    type_part, speed_part = tmp.strip().upper().split("-")
                    comp["type"] = type_part
                    comp["speed"] = speed_part

                comp["latency"] = None
                # print(f"RAM: {comp}")

            if category_name == "power_supply":
                comp.update(extract_brand_from_power_supply(title))
                watt_element = item.select_one("span.watt")
                if watt_element is not None:
                    comp["maxPowerWatt"] = int(watt_element.text.replace("W", ""))
                    # print(comp["maxPowerWatt"])
                else:
                    comp["maxPowerWatt"] = None


            if category_name == "motherboard":

                # Limit to first 50 offers for testing
                if i > 100:
                    break

                comp.update(extract_brand_from_motherboard(title))
                comp["socket_motherboard"] = item.select_one("span.socket").text
                comp["format"] = item.select_one("span.size").text
                comp["chipset"] = item.select_one("span.chipset").text

                # Extract link to detailed page
                link_element = item.find("a")
                if link_element and link_element.get("href"):
                    detail_url = link_element["href"]
                    if not detail_url.startswith("http"):
                        detail_url = "https://www.pc-kombo.com" + detail_url

                    # Navigate to detailed page
                    try:
                        detail_page = await page.browser.get(detail_url)
                        await asyncio.sleep(1)  # Wait longer for page to load

                        detail_html = await detail_page.get_content()
                        detail_soup = BeautifulSoup(detail_html, "html.parser")

                        # Check for card-body elements
                        card_bodies = detail_soup.select("div.card-body")

                        # Try different selectors for the memory information
                        memory_info_found = False

                        # Method 1: Look for card-body with dl elements
                        for card_body in card_bodies:
                            dl_elements = card_body.find_all("dl")

                            for dl in dl_elements:
                                dt_elements = dl.find_all("dt")
                                dd_elements = dl.find_all("dd")

                                for dt, dd in zip(dt_elements, dd_elements):
                                    dt_text = dt.text.strip()
                                    dd_text = dd.text.strip()

                                    if dt_text == "Memory Type":
                                        comp["memory_type"] = dd_text
                                        memory_info_found = True
                                    elif dt_text == "Memory Capacity":
                                        if dd_text.isdigit():
                                            comp["memory_capacity"] = int(dd_text)
                                        else:
                                            comp["memory_capacity"] = dd_text
                                        memory_info_found = True
                                    elif dt_text == "Ramslots":
                                        if dd_text.isdigit():
                                            comp["ramslots"] = int(dd_text)
                                        else:
                                            comp["ramslots"] = dd_text
                                        memory_info_found = True

                        # Method 2: If not found, try looking for any dl elements on the page
                        if not memory_info_found:
                            all_dls = detail_soup.find_all("dl")

                            for dl in all_dls:
                                dt_elements = dl.find_all("dt")
                                dd_elements = dl.find_all("dd")

                                for dt, dd in zip(dt_elements, dd_elements):
                                    dt_text = dt.text.strip()
                                    dd_text = dd.text.strip()

                                    if dt_text == "Memory Type":
                                        comp["memory_type"] = dd_text
                                        memory_info_found = True
                                    elif dt_text == "Memory Capacity":
                                        if dd_text.isdigit():
                                            comp["memory_capacity"] = int(dd_text)
                                        else:
                                            comp["memory_capacity"] = dd_text
                                        memory_info_found = True
                                    elif dt_text == "Ramslots":
                                        if dd_text.isdigit():
                                            comp["ramslots"] = int(dd_text)
                                        else:
                                            comp["ramslots"] = dd_text
                                        memory_info_found = True

                        if not memory_info_found:
                            # Set default values
                            comp["memory_type"] = None
                            comp["memory_capacity"] = None
                            comp["ramslots"] = None

                    except Exception as e:
                        print(f"Error extracting detailed motherboard info from {detail_url}: {e}")
                        comp["memory_type"] = None
                        comp["memory_capacity"] = None
                        comp["ramslots"] = None
                else:
                    comp["memory_type"] = None
                    comp["memory_capacity"] = None
                    comp["ramslots"] = None

            if category_name == "cpu_cooler":
                comp.update(extract_brand_from_cpu_cooler(title))

                tmp = item.select_one("span.sockets").text
                pattern = r"\b(?:\d{3,4}(?:-v\d)?|am\d\+?|fm\d\+?)\b"
                sockets = re.findall(pattern, tmp.lower())
                comp["sockets"] = sockets
                # print(f"CPU Cooler: {comp}")

            # print(comp)
            # print("\n")
            if comp["brand"] is not None:
                comp["category"] = category_name
                print(f"Adding component: {comp}")
                print("\n")

                all_components[category_name].append(comp)

        except Exception as e:
            print(f"{i}. Błąd: {e}")
    print(len(all_components[category_name]))
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
    print(len(all_components))
    
    # Save to CSV files
    save_to_csv(all_components)
    
    return all_components


def save_to_csv(components):
    """Save components to separate CSV files by category"""
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Group components by category
    grouped = {}
    for comp in components:
        category = comp.get('category')
        if category:
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(comp)
    
    # Define CSV headers for each category
    csv_configs = {
        'processor': {
            'filename': 'processors.csv',
            'headers': ['brand', 'model', 'cores', 'threads', 'socket', 'base_clock', 'boost_clock', 'integrated_graphics', 'tdp'],
            'mapper': lambda c: {
                'brand': c.get('brand', ''),
                'model': c.get('model', ''),
                'cores': c.get('cores', ''),
                'threads': c.get('threads', ''),
                'socket': c.get('socket', ''),
                'base_clock': c.get('base_clock', ''),
                'boost_clock': '',  # Not scraped
                'integrated_graphics': '',  # Not scraped
                'tdp': ''  # Not scraped
            }
        },
        'graphics_card': {
            'filename': 'graphics_cards.csv',
            'headers': ['brand', 'model', 'vram', 'gddr', 'boost_clock', 'core_clock', 'power_draw', 'length_in_mm'],
            'mapper': lambda c: {
                'brand': c.get('brand', ''),
                'model': c.get('model', ''),
                'vram': c.get('vram', ''),
                'gddr': c.get('gddr', ''),
                'boost_clock': '',  # Not scraped
                'core_clock': '',  # Not scraped
                'power_draw': c.get('power_draw', ''),
                'length_in_mm': ''  # Not scraped
            }
        },
        'ram': {
            'filename': 'memory.csv',
            'headers': ['brand', 'model', 'type', 'capacity', 'speed', 'latency', 'amount'],
            'mapper': lambda c: {
                'brand': c.get('brand', ''),
                'model': c.get('model', ''),
                'type': c.get('type', ''),
                'capacity': c.get('capacity', ''),
                'speed': c.get('speed', ''),
                'latency': c.get('latency', ''),
                'amount': ''  # Not scraped
            }
        },
        'case': {
            'filename': 'cases.csv',
            'headers': ['brand', 'model', 'format'],
            'mapper': lambda c: {
                'brand': c.get('brand', ''),
                'model': c.get('model', ''),
                'format': c.get('format', '')
            }
        },
        'ssd': {
            'filename': 'storage.csv',
            'headers': ['brand', 'model', 'capacity'],
            'mapper': lambda c: {
                'brand': c.get('brand', ''),
                'model': c.get('model', ''),
                'capacity': c.get('capacity', '')
            }
        },
        'power_supply': {
            'filename': 'power_supplies.csv',
            'headers': ['brand', 'model', 'modular', 'type', 'efficiency_rating', 'max_power_watt'],
            'mapper': lambda c: {
                'brand': c.get('brand', ''),
                'model': c.get('model', ''),
                'modular': '',  # Not scraped
                'type': '',  # Not scraped
                'efficiency_rating': '',  # Not scraped
                'max_power_watt': c.get('maxPowerWatt', '')
            }
        },
        'cpu_cooler': {
            'filename': 'coolers.csv',
            'headers': ['brand', 'model', 'cooler_sockets_type', 'fan_rpm', 'noise_level', 'radiator_size'],
            'mapper': lambda c: {
                'brand': c.get('brand', ''),
                'model': c.get('model', ''),
                'cooler_sockets_type': ';'.join(c.get('sockets', [])) if c.get('sockets') else '',
                'fan_rpm': '',  # Not scraped
                'noise_level': '',  # Not scraped
                'radiator_size': ''  # Not scraped
            }
        },
        'motherboard': {
            'filename': 'motherboards.csv',
            'headers': ['brand', 'model', 'chipset', 'socket_type', 'format', 'ram_slots', 'ram_capacity', 'memory_type'],
            'mapper': lambda c: {
                'brand': c.get('brand', ''),
                'model': c.get('model', ''),
                'chipset': c.get('chipset', ''),
                'socket_type': c.get('socket_motherboard', ''),
                'format': c.get('format', ''),
                'ram_slots': c.get('ramslots', ''),
                'ram_capacity': c.get('memory_capacity', ''),
                'memory_type': c.get('memory_type', '')
            }
        }
    }
    
    # Write CSV files
    for category, items in grouped.items():
        if category not in csv_configs:
            print(f"Warning: No CSV config for category '{category}'")
            continue
            
        config = csv_configs[category]
        filepath = os.path.join(output_dir, config['filename'])
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=config['headers'])
                writer.writeheader()
                
                for item in items:
                    row = config['mapper'](item)
                    writer.writerow(row)
            
            print(f"Saved {len(items)} items to {filepath}")
        except Exception as e:
            print(f"Error writing CSV for {category}: {e}")


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

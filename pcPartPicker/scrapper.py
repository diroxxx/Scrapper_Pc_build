import asyncio
import sys
import os
import nodriver as uc
import re
import random
from bs4 import BeautifulSoup

# Add parent directory to Python path to find validComponentsApi
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

CATEGORIES = {
    # "processor": "https://pcpartpicker.com/products/cpu/",
    "cpu_cooler": "https://pcpartpicker.com/products/cpu-cooler/",
    # "motherboard": "https://pcpartpicker.com/products/motherboard/",
    # "storage": "https://pcpartpicker.com/products/internal-hard-drive/",
    # "graphics_card": "https://pcpartpicker.com/products/video-card/",
    # "ram": "https://pcpartpicker.com/products/memory/",
    # "case": "https://pcpartpicker.com/products/case/",
    # "power_supply": "https://pcpartpicker.com/products/power-supply/",
}


async def random_delay(min_seconds=1, max_seconds=3):
    """Add random delay to avoid detection"""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


def extract_processor_specs(soup):
    """Extract processor specifications from PCPartPicker HTML structure"""
    specs = {}
    cpu_info = {}
    
    # Find all specification groups
    spec_groups = soup.select('.group.group--spec')
    print(f"Found {len(spec_groups)} specification groups")
    
    for group in spec_groups:
        # Extract title
        title_element = group.select_one('.group__title')
        if not title_element:
            continue
            
        title = title_element.get_text(strip=True)
        
        # Extract content
        content_element = group.select_one('.group__content')
        if not content_element:
            continue
        
        # Check if content has a list (multiple values)
        list_items = content_element.select('li')
        if list_items:
            # Multiple values - join them with commas
            values = [item.get_text(strip=True) for item in list_items]
            specs[title] = ', '.join(values)
        else:
            # Single value - get text from p tag or direct text
            p_element = content_element.select_one('p')
            if p_element:
                specs[title] = p_element.get_text(strip=True)
            else:
                specs[title] = content_element.get_text(strip=True)

    # print(f"Raw specs extracted: {specs}")
    
    # Extract only the specific specs we need
    needed_specs = ['Maximum Supported Memory', 'Performance Core Clock', 'Core Count', 'Thread Count', 'Socket', 'Manufacturer', 'Model']
    
    for spec_name in needed_specs:
        if spec_name in specs:
            cpu_info[spec_name.lower().replace(' ', '_')] = specs[spec_name]
            print(f"{spec_name}: {specs[spec_name]}")
    
    # print(f"Final CPU info: {cpu_info}")
    # print("\n")
    return cpu_info


def extract_storage_specs(soup):
    """Extract storage specifications from PCPartPicker HTML structure"""
    specs = {}
    storage_info = {}
    
    # Find all specification groups
    spec_groups = soup.select('.group.group--spec')
    print(f"Found {len(spec_groups)} specification groups")
    
    for group in spec_groups:
        # Extract title
        title_element = group.select_one('.group__title')
        if not title_element:
            continue
            
        title = title_element.get_text(strip=True)
        
        # Extract content
        content_element = group.select_one('.group__content')
        if not content_element:
            continue
        
        # Check if content has a list (multiple values)
        list_items = content_element.select('li')
        if list_items:
            # Multiple values - join them with commas
            values = [item.get_text(strip=True) for item in list_items]
            specs[title] = ', '.join(values)
        else:
            # Single value - get text from p tag or direct text
            p_element = content_element.select_one('p')
            if p_element:
                specs[title] = p_element.get_text(strip=True)
            else:
                specs[title] = content_element.get_text(strip=True)
    
    # Extract only the specific specs we need for storage
    needed_specs = ['Manufacturer', 'Capacity', 'Type', 'Form Factor', 'Model']
    
    for spec_name in needed_specs:
        if spec_name in specs:
            storage_info[spec_name.lower().replace(' ', '_')] = specs[spec_name]
    
    return storage_info


def extract_cpu_cooler_specs(soup):
    """Extract CPU cooler specifications from PCPartPicker HTML structure"""
    specs = {}
    cooler_info = {}
    
    # Find all specification groups
    spec_groups = soup.select('.group.group--spec')
    print(f"Found {len(spec_groups)} specification groups")
    
    for group in spec_groups:
        # Extract title
        title_element = group.select_one('.group__title')
        if not title_element:
            continue
            
        title = title_element.get_text(strip=True)
        
        # Extract content
        content_element = group.select_one('.group__content')
        if not content_element:
            continue
        
        # Check if content has a list (multiple values)
        list_items = content_element.select('li')
        if list_items:
            # Multiple values - join them with commas
            values = [item.get_text(strip=True) for item in list_items]
            specs[title] = ', '.join(values)
        else:
            # Single value - get text from p tag or direct text
            p_element = content_element.select_one('p')
            if p_element:
                specs[title] = p_element.get_text(strip=True)
            else:
                specs[title] = content_element.get_text(strip=True)
    
    # Extract only the specific specs we need for CPU coolers
    needed_specs = ['Manufacturer', 'CPU Socket', 'Model']
    
    for spec_name in needed_specs:
        if spec_name in specs:
            cooler_info[spec_name.lower().replace(' ', '_')] = specs[spec_name]
    
    return cooler_info


def extract_motherboard_specs(soup):
    """Extract motherboard specifications from PCPartPicker HTML structure"""
    specs = {}
    motherboard_info = {}
    
    # Find all specification groups
    spec_groups = soup.select('.group.group--spec')
    print(f"Found {len(spec_groups)} specification groups")
    
    for group in spec_groups:
        # Extract title
        title_element = group.select_one('.group__title')
        if not title_element:
            continue
            
        title = title_element.get_text(strip=True)
        
        # Extract content
        content_element = group.select_one('.group__content')
        if not content_element:
            continue
        
        # Check if content has a list (multiple values)
        list_items = content_element.select('li')
        if list_items:
            # Multiple values - join them with commas
            values = [item.get_text(strip=True) for item in list_items]
            specs[title] = ', '.join(values)
        else:
            # Single value - get text from p tag or direct text
            p_element = content_element.select_one('p')
            if p_element:
                specs[title] = p_element.get_text(strip=True)
            else:
                specs[title] = content_element.get_text(strip=True)
    
    # Extract only the specific specs we need for motherboards
    needed_specs = ['Manufacturer', 'Socket / CPU', 'Form Factor', 'Chipset', 'Memory Type', 'Memory Slots', 'Model']
    
    for spec_name in needed_specs:
        if spec_name in specs:
            motherboard_info[spec_name.lower().replace(' ', '_').replace('/', '_')] = specs[spec_name]
    
    return motherboard_info


def extract_memory_specs(soup):
    """Extract memory specifications from PCPartPicker HTML structure"""
    specs = {}
    memory_info = {}
    
    # Find all specification groups
    spec_groups = soup.select('.group.group--spec')
    print(f"Found {len(spec_groups)} specification groups")
    
    for group in spec_groups:
        # Extract title
        title_element = group.select_one('.group__title')
        if not title_element:
            continue
            
        title = title_element.get_text(strip=True)
        
        # Extract content
        content_element = group.select_one('.group__content')
        if not content_element:
            continue
        
        # Check if content has a list (multiple values)
        list_items = content_element.select('li')
        if list_items:
            # Multiple values - join them with commas
            values = [item.get_text(strip=True) for item in list_items]
            specs[title] = ', '.join(values)
        else:
            # Single value - get text from p tag or direct text
            p_element = content_element.select_one('p')
            if p_element:
                specs[title] = p_element.get_text(strip=True)
            else:
                specs[title] = content_element.get_text(strip=True)
    
    # Extract only the specific specs we need for memory
    needed_specs = ['Manufacturer', 'Speed', 'Model']
    
    for spec_name in needed_specs:
        if spec_name in specs:
            memory_info[spec_name.lower().replace(' ', '_')] = specs[spec_name]
    
    return memory_info


def extract_graphics_card_specs(soup):
    """Extract graphics card specifications from PCPartPicker HTML structure"""
    specs = {}
    gpu_info = {}
    
    # Find all specification groups
    spec_groups = soup.select('.group.group--spec')
    print(f"Found {len(spec_groups)} specification groups")
    
    for group in spec_groups:
        # Extract title
        title_element = group.select_one('.group__title')
        if not title_element:
            continue
            
        title = title_element.get_text(strip=True)
        
        # Extract content
        content_element = group.select_one('.group__content')
        if not content_element:
            continue
        
        # Check if content has a list (multiple values)
        list_items = content_element.select('li')
        if list_items:
            # Multiple values - join them with commas
            values = [item.get_text(strip=True) for item in list_items]
            specs[title] = ', '.join(values)
        else:
            # Single value - get text from p tag or direct text
            p_element = content_element.select_one('p')
            if p_element:
                specs[title] = p_element.get_text(strip=True)
            else:
                specs[title] = content_element.get_text(strip=True)
    
    # Extract only the specific specs we need for graphics cards
    needed_specs = ['Manufacturer', 'Memory', 'Core Clock', 'Memory Type', 'Model', 'TDP']
    
    for spec_name in needed_specs:
        if spec_name in specs:
            gpu_info[spec_name.lower().replace(' ', '_')] = specs[spec_name]
    
    return gpu_info


def extract_power_supply_specs(soup):
    """Extract power supply specifications from PCPartPicker HTML structure"""
    specs = {}
    psu_info = {}
    
    # Find all specification groups
    spec_groups = soup.select('.group.group--spec')
    print(f"Found {len(spec_groups)} specification groups")
    
    for group in spec_groups:
        # Extract title
        title_element = group.select_one('.group__title')
        if not title_element:
            continue
            
        title = title_element.get_text(strip=True)
        
        # Extract content
        content_element = group.select_one('.group__content')
        if not content_element:
            continue
        
        # Check if content has a list (multiple values)
        list_items = content_element.select('li')
        if list_items:
            # Multiple values - join them with commas
            values = [item.get_text(strip=True) for item in list_items]
            specs[title] = ', '.join(values)
        else:
            # Single value - get text from p tag or direct text
            p_element = content_element.select_one('p')
            if p_element:
                specs[title] = p_element.get_text(strip=True)
            else:
                specs[title] = content_element.get_text(strip=True)
    
    # Extract only the specific specs we need for power supplies
    needed_specs = ['Manufacturer', 'Type', 'Efficiency Rating', 'Wattage', 'Modular', 'Model']
    
    for spec_name in needed_specs:
        if spec_name in specs:
            psu_info[spec_name.lower().replace(' ', '_')] = specs[spec_name]
    
    return psu_info


def clean_model_name(title, manufacturer, category_name):
    """Clean the title to create a model name by removing manufacturer and component-specific terms"""
    if not title:
        return ""
    
    cleaned_title = title
    
    # Remove manufacturer name if present
    if manufacturer:
        cleaned_title = re.sub(rf'\b{re.escape(manufacturer)}\b', '', cleaned_title, flags=re.IGNORECASE).strip()
    
    # Remove category-specific terms
    category_terms = {
        'processor': ['CPU', 'Processor', 'Desktop Processor'],
        'cpu_cooler': ['CPU Cooler', 'Cooler', 'Air Cooler', 'Liquid Cooler'],
        'motherboard': ['Motherboard', 'ATX', 'Mini-ITX', 'Micro-ATX'],
        'storage': ['SSD', 'HDD', 'Hard Drive', 'Solid State Drive', 'NVMe', 'M.2'],
        'graphics_card': ['Graphics Card', 'Video Card', 'GPU'],
        'ram': ['Memory', 'RAM', 'DDR4', 'DDR5'],
        'power_supply': ['Power Supply', 'PSU', 'Modular', 'Semi-Modular', 'Non-Modular'],
        'case': ['Case', 'Tower', 'Mid Tower', 'Full Tower', 'Mini-ITX']
    }
    
    if category_name in category_terms:
        for term in category_terms[category_name]:
            cleaned_title = re.sub(rf'\b{re.escape(term)}\b', '', cleaned_title, flags=re.IGNORECASE).strip()
    
    # Clean up extra spaces and hyphens
    cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
    cleaned_title = re.sub(r'^[-\s]+|[-\s]+$', '', cleaned_title)
    
    return cleaned_title


async def extract_component_info(soup, category_name):
    """Extract component information based on category"""
    try:
        component_info = {}
        
        # Extract basic info that's common across all categories
        name_element = soup.select_one('h1') or soup.select_one('.pageTitle') or soup.select_one('[data-title]')
        if name_element:
            component_info['name'] = name_element.get_text(strip=True)
        
        # Category-specific extraction
        if category_name == "processor":
            cpu_info = extract_processor_specs(soup)
            component_info.update(cpu_info)
        elif category_name == "cpu_cooler":
            cooler_info = extract_cpu_cooler_specs(soup)
            component_info.update(cooler_info)
        elif category_name == "motherboard":
            motherboard_info = extract_motherboard_specs(soup)
            component_info.update(motherboard_info)
        elif category_name == "ram":
            memory_info = extract_memory_specs(soup)
            component_info.update(memory_info)
        elif category_name == "storage":
            storage_info = extract_storage_specs(soup)
            component_info.update(storage_info)
        elif category_name == "graphics_card":
            gpu_info = extract_graphics_card_specs(soup)
            component_info.update(gpu_info)
        elif category_name == "power_supply":
            psu_info = extract_power_supply_specs(soup)
            component_info.update(psu_info)
        else:
            # For other categories, use the old table extraction method
            specs = {}
            spec_table = soup.select('.group--specification tr')
            for row in spec_table:
                cells = row.select('td')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    specs[key] = value
            component_info['specifications'] = specs
        
        # Always create cleaned model name from the title, overriding any extracted "Model" spec
        if 'name' in component_info:
            manufacturer = component_info.get('manufacturer', '')
            cleaned_model = clean_model_name(component_info['name'], manufacturer, category_name)
            component_info['model'] = cleaned_model
            
            # Remove the original "Model" field if it was extracted from specs (since it's usually just the full title)
            if 'model' in component_info and component_info['model'] != cleaned_model:
                component_info['model'] = cleaned_model
        
        print(f"Extracted {category_name} component: {component_info.get('name', 'Unknown')}")  
        
        return component_info
    
    except Exception as e:
        print(f"Błąd podczas wyodrębniania informacji o komponencie: {e}")
        return None


async def scrape_category(browser, page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}

    # Scroll to load more content
    for i in range(10):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await random_delay(0.5, 1.5)
    
    await random_delay(2, 4)

    html = await page.get_content()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("tr")
    print(f"Znaleziono {len(cards)} ofert w kategorii {category_name}:\n")

    component_links = []
    
    # First, collect all links
    for item in cards:
        try:
            link_element = item.select_one("a")
            if link_element and link_element.get("href"):
                a = link_element.attrs["href"]
                if a.startswith('/'):
                    link = "https://pcpartpicker.com" + a
                    component_links.append(link)
        except Exception as e:
            continue
    
    print(f"Znaleziono {len(component_links)} linków do komponentów")
    
    # Process links with delays
    for i, link in enumerate(component_links, start=1):
        try:
            print(f"\n{'='*60}")
            # print(f"Processing {i}/{min(5, len(component_links))}")
            print(f"Link: {link}")
            print(f"{'='*60}")
            
            # Use the same browser instance but navigate to new page
            component_page = await browser.get(link)
            await random_delay(2, 4)  # Wait for page to load
            
            html2 = await component_page.get_content()
            soup2 = BeautifulSoup(html2, "html.parser")
            
            # Extract component information
            component_info = await extract_component_info(soup2, category_name)
            if component_info:
                print(f"Title: {component_info.get('name', 'Unknown')}")
                print(f"Specifications:")
                for key, value in component_info.items():
                    if key != 'name':
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                
                all_components[category_name].append(component_info)
                print(f"✓ Component added successfully!")
            else:
                print("❌ Failed to extract component info")
            
            # Add delay between requests
            await random_delay(3, 6)

        except Exception as e:
            print(f"❌ Error processing {link}: {e}")
            await random_delay(2, 4) # Even on error, wait before continuing

    print(f"Znaleziono {len(all_components[category_name])} komponentów w kategorii {category_name}.\n")
    return all_components


async def main():
    all_components_by_category = {}
    
    # Configure browser with more human-like settings
    browser = await uc.start(
        headless=False,  # Keep visible for debugging, set to True for production
        user_data_dir=None,  # Use temporary profile
        browser_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions-http-throttling"
        ]
    )
    
    try:
        for category_name, url in CATEGORIES.items():
            print(f"\n=== Pobieram kategorię: {category_name} ===")
            
            try:
                page = await browser.get(url)
                await random_delay(5, 8)  # Wait for page to fully load
                
                items = await scrape_category(browser, page, category_name)
                
                # Map category names to more readable keys
                category_key_map = {
                    "processor": "processor",
                    "cpu_cooler": "cpuCooler", 
                    "motherboard": "motherboard",
                    "storage": "storage",
                    "graphics_card": "graphicsCard",
                    "ram": "ram",
                    "case": "case",
                    "power_supply": "powerSupply"
                }
                
                mapped_key = category_key_map.get(category_name, category_name)
                all_components_by_category[mapped_key] = items[category_name]
                
                print(f"Zakończono kategorię {category_name}. Pobranych komponentów: {len(items[category_name])}")
                
                # Longer delay between categories
                await random_delay(10, 15)
                
            except Exception as e:
                print(f"Błąd podczas przetwarzania kategorii {category_name}: {e}")
                await random_delay(5, 10)

    finally:
        if browser:
            browser.stop()
    
    # Print summary
    total_components = sum(len(components) for components in all_components_by_category.values())
    print(f"\n=== PODSUMOWANIE ===")
    for category, components in all_components_by_category.items():
        print(f"{category}: {len(components)} komponentów")
    print(f"Łączna liczba pobranych komponentów: {total_components}")
    
    return all_components_by_category


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

import asyncio
import sys
import os
import nodriver as uc
import re
import random
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# Add parent directory to Python path to find validComponentsApi
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

CATEGORIES = {
    # "processor": "https://pcpartpicker.com/products/cpu/",
    # "cpu_cooler": "https://pcpartpicker.com/products/cpu-cooler/",
    "motherboard": "https://pcpartpicker.com/products/motherboard/",
    "storage": "https://pcpartpicker.com/products/internal-hard-drive/",
    "graphics_card": "https://pcpartpicker.com/products/video-card/",
    "ram": "https://pcpartpicker.com/products/memory/",
    "case": "https://pcpartpicker.com/products/case/",
    "power_supply": "https://pcpartpicker.com/products/power-supply/",
}


async def random_delay(min_seconds=1, max_seconds=3):
    """Add random delay to avoid detection"""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


def extract_processor_specs_from_row(row):
    """Extract processor specifications from table row"""
    specs = {}
    
    # Extract name
    name_element = row.select_one('.td__name p')
    if name_element:
        specs['name'] = name_element.get_text(strip=True)
    
    # Extract all spec cells
    spec_cells = row.select('.td__spec')
    for cell in spec_cells:
        label = cell.select_one('.specLabel')
        if label:
            key = label.get_text(strip=True)
            # Get value (everything except the label)
            label.extract()
            value = cell.get_text(strip=True)
            
            # Map to our field names
            field_map = {
                'Core Count': 'core_count',
                'Performance Core Clock': 'performance_core_clock',
                'Performance Core Boost Clock': 'performance_boost_clock',
                'Microarchitecture': 'microarchitecture',
                'TDP': 'tdp',
                'Integrated Graphics': 'integrated_graphics'
            }
            
            if key in field_map:
                specs[field_map[key]] = value
    
    # Extract manufacturer from name (usually first word)
    if 'name' in specs:
        parts = specs['name'].split()
        if parts:
            specs['manufacturer'] = parts[0]
            # Model is everything after manufacturer
            specs['model'] = ' '.join(parts[1:]) if len(parts) > 1 else specs['name']
    
    return specs


def extract_component_info_from_row(row, category_name):
    """Extract component information from table row based on category"""
    try:
        component_info = {}
        
        # Category-specific extraction
        if category_name == "processor":
            component_info = extract_processor_specs_from_row(row)
        # Add other categories here as needed
        else:
            # Generic extraction for other categories
            name_element = row.select_one('.td__name p')
            if name_element:
                component_info['name'] = name_element.get_text(strip=True)
            
            spec_cells = row.select('.td__spec')
            for cell in spec_cells:
                label = cell.select_one('.specLabel')
                if label:
                    key = label.get_text(strip=True).lower().replace(' ', '_')
                    label.extract()
                    value = cell.get_text(strip=True)
                    component_info[key] = value
        
        return component_info if component_info else None
    
    except Exception as e:
        print(f"Error extracting component info from row: {e}")
        return None


async def scrape_category(browser, page, category_name):
    all_components = {cat: [] for cat in CATEGORIES}
    current_page = 1
    has_more_pages = True

    while has_more_pages:
        print(f"\n{'#'*60}")
        print(f"Scraping page {current_page} of category {category_name}")
        print(f"{'#'*60}")
        
        # Scroll to load more content
        for i in range(10):
            await page.evaluate("window.scrollBy(0, window.innerHeight);")
            await random_delay(0.5, 1.5)
        
        await random_delay(2, 4)

        html = await page.get_content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all product rows
        rows = soup.select("tr.tr__product")
        print(f"Found {len(rows)} products on page {current_page}\n")

        if len(rows) == 0:
            print("No more products found. Ending pagination.")
            has_more_pages = False
            break

        # Process each row directly
        for i, row in enumerate(rows, start=1):
            try:
                print(f"\n{'='*60}")
                print(f"Processing product {i}/{len(rows)} on page {current_page}")
                print(f"{'='*60}")
                
                # Extract component information from the row
                component_info = extract_component_info_from_row(row, category_name)
                
                if component_info:
                    print(f"Name: {component_info.get('name', 'Unknown')}")
                    print(f"Specifications:")
                    for key, value in component_info.items():
                        if key != 'name':
                            print(f"  {key.replace('_', ' ').title()}: {value}")
                    
                    all_components[category_name].append(component_info)
                    print(f"✓ Component added successfully!")
                else:
                    print("❌ Failed to extract component info")

            except Exception as e:
                print(f"❌ Error processing row: {e}")

        # Check if there's a next page in pagination
        # Look for the next page number (current + 1)
        next_page_num = current_page + 1
        next_page_link = soup.select_one(f'ul.pagination a[href="#page={next_page_num}"]')
        
        if next_page_link:
            print(f"\n→ Moving to page {next_page_num}")
            
            # Click on the next page link using JavaScript
            try:
                # Find and click the link on the actual page
                await page.evaluate(f'''
                    const link = document.querySelector('a[href="#page={next_page_num}"]');
                    if (link) {{
                        link.click();
                    }}
                ''')
                
                # Wait for page to load
                await random_delay(3, 6)
                
                # Scroll to top to ensure content loads
                await page.evaluate("window.scrollTo(0, 0);")
                await random_delay(1, 2)
                
                current_page += 1
            except Exception as e:
                print(f"Error clicking next page: {e}")
                has_more_pages = False
        else:
            print(f"\nNo page {next_page_num} found in pagination. Ending.")
            has_more_pages = False

    print(f"\nTotal found: {len(all_components[category_name])} components in category {category_name} across {current_page} page(s).\n")
    return all_components


def save_to_csv(components, category_name):
    """Save components to CSV file"""
    if not components:
        print(f"No components to save for {category_name}")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(current_dir, "scraped_data")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"{category_name}_{timestamp}.csv")
    
    # Get all unique keys from all components to create column headers
    all_keys = set()
    for component in components:
        all_keys.update(component.keys())
    
    # Sort keys to have consistent column order (name and manufacturer first)
    priority_keys = ['name', 'manufacturer', 'model']
    sorted_keys = [k for k in priority_keys if k in all_keys]
    sorted_keys.extend(sorted([k for k in all_keys if k not in priority_keys]))
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted_keys)
        writer.writeheader()
        writer.writerows(components)
    
    print(f"\n✓ Saved {len(components)} components to {filename}")


async def main():
    all_components_by_category = {}
    
    # Configure browser with more human-like settings
    browser = await uc.start(
        headless=False,
        user_data_dir=None,
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
            print(f"\n=== Scraping category: {category_name} ===")
            
            try:
                page = await browser.get(url)
                await random_delay(5, 8) 
                
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
                
                # Save to CSV after scraping each category
                save_to_csv(items[category_name], category_name)
                
                print(f"Completed category {category_name}. Components scraped: {len(items[category_name])}")
                
                # Longer delay between categories
                await random_delay(10, 15)
                
            except Exception as e:
                print(f"Error processing category {category_name}: {e}")
                await random_delay(5, 10)

    finally:
        if browser:
            browser.stop()
    
    # Print summary
    total_components = sum(len(components) for components in all_components_by_category.values())
    print(f"\n=== SUMMARY ===")
    for category, components in all_components_by_category.items():
        print(f"{category}: {len(components)} components")
    print(f"Total components scraped: {total_components}")
    
    return all_components_by_category


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

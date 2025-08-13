import time

from flask import Flask, jsonify
import asyncio
import sys
import os

# Add parent directory to Python path to find pcPartPicker scrapper
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
pcpartpicker_dir = os.path.join(parent_dir, 'pcPartPicker')
sys.path.insert(0, pcpartpicker_dir)

# import itemComponentScrapper
import pcPartPicker.scrapper as scrapper
app = Flask(__name__)

CATEGORIES = [
    "processor", "graphics_card", "ram", "case", "storage", "power_supply", "motherboard", "cpu_cooler"
]

@app.route('/installComponents', methods=['GET'])
def get_comp():
    all_components = {cat: [] for cat in CATEGORIES}

    start_time = time.perf_counter()

    try:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        pc_kombo_components = loop.run_until_complete(scrapper.main())
        loop.close()
        
        # PCPartPicker scrapper returns dict with category keys, so merge them
        for category_key, components in pc_kombo_components.items():
            # Map PCPartPicker category keys to our expected categories
            category_mapping = {
                "processor": "processor",
                "cpuCooler": "cpu_cooler", 
                "motherboard": "motherboard",
                "storage": "storage",
                "graphicsCard": "graphics_card",
                "ram": "ram",
                "case": "case",
                "powerSupply": "power_supply"
            }
            
            mapped_category = category_mapping.get(category_key)
            if mapped_category and mapped_category in all_components:
                all_components[mapped_category].extend(components)


        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        total_items = sum(len(components) for components in all_components.values())
        print(f"returned {total_items} total items")
        print(f"Total execution time: {execution_time:.2f} seconds")
        print(f"Total execution time: {execution_time / 60:.2f} minutes")

        return jsonify(all_components)

    except Exception as e:
        print(f"Error in get_comp(): {e}")
        return jsonify({"error": f"Failed to scrape data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

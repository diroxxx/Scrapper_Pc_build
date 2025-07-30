import time

from flask import Flask, jsonify, request
import asyncio

import itemComponentScrapper
app = Flask(__name__)

CATEGORIES = [
    "processor", "graphics_card", "ram", "case", "storage", "power_supply", "motherboard"
]

@app.route('/installComponents', methods=['GET'])
def get_comp():
    all_components = {cat: [] for cat in CATEGORIES}

    start_time = time.perf_counter()

    try:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        pc_kombo_components = loop.run_until_complete(itemComponentScrapper.main())
        loop.close()

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        print(f"OLX returned {len(pc_kombo_components)} total items")
        print(f"Total execution time: {execution_time:.2f} seconds")
        print(f"Total execution time: {execution_time / 60:.2f} minutes")


        # Merge into all_components
        # for cat in CATEGORIES:
        #     all_components[cat].extend([item for item in data_olx if item['category'] == cat])
        #     all_components[cat].extend([item for item in data_allegro_lokalnie if item['category'] == cat])
        #     all_components[cat].extend([item for item in data_allegro if item['category'] == cat])

        return jsonify(pc_kombo_components)
        # return jsonify(all_components)

    except Exception as e:
        print(f"Error in get_comp(): {e}")
        return jsonify({"error": f"Failed to scrape data: {str(e)}"}), 500
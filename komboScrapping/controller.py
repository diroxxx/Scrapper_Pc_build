import time

from flask import Flask, jsonify
import asyncio

import scrapper

app = Flask(__name__)

CATEGORIES = [
    "processor",
    "graphics_card",
    "ram", "case",
    "storage",
    "power_supply",
    "motherboard",
    "cpu_cooler"
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
        for cat in CATEGORIES:
            all_components[cat].extend([item for item in pc_kombo_components if item['category'] == cat])

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        # print(pc_kombo_components)
        print(f"returned {len(pc_kombo_components)} total items")
        print(f"Total execution time: {execution_time:.2f} seconds")
        print(f"Total execution time: {execution_time / 60:.2f} minutes")

        return jsonify(all_components)
        # return jsonify(all_components)

    except Exception as e:
        print(f"Error in get_comp(): {e}")
        return jsonify({"error": f"Failed to scrape data: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)

import time

from flask import Flask, jsonify, request
import asyncio

import olxApi
import allegroApi
import allegroLokalneApi

# import xkomApi  # Commented out as it's incomplete

app = Flask(__name__)

CATEGORIES = [
    "processor", "graphics_card", "ram", "case", "storage", "power_supply", "motherboard"
]

@app.route('/installComponents', methods=['GET'])
def get_comp():
    """Get components from OLX organized by category"""
    all_components = {cat: [] for cat in CATEGORIES}

    start_time = time.perf_counter()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("Starting to scrape OLX...")
        data_olx = loop.run_until_complete(olxApi.main())
        print("Starting to scrape Allegro lokalne...")
        data_allegro_lokalnie = loop.run_until_complete(allegroLokalneApi.main())
        print("Starting to scrape Allegro...")
        data_allegro = loop.run_until_complete(allegroApi.main())
        loop.close()

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        print(f"OLX returned {len(data_olx)} total items")
        print(f"allegroLok returned {len(data_allegro_lokalnie)} total items")
        print(f"allegro returned {len(data_allegro)} total items")
        print(f"Total execution time: {execution_time:.2f} seconds")
        print(f"Total execution time: {execution_time / 60:.2f} minutes")


        # Merge into all_components
        for cat in CATEGORIES:
            all_components[cat].extend([item for item in data_olx if item['category'] == cat])
            all_components[cat].extend([item for item in data_allegro_lokalnie if item['category'] == cat])
            all_components[cat].extend([item for item in data_allegro if item['category'] == cat])

        return jsonify(all_components)

    except Exception as e:
        print(f"Error in get_comp(): {e}")
        return jsonify({"error": f"Failed to scrape data: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "PC Build Scraper API is running"})

import logging
@app.route('/', methods=['GET'])
def home():
    """API documentation endpoint"""

    logging.warning("Request received!")
    return jsonify({
        "message": "PC Build Scraper API",
        "endpoints": {
            "/components": "Get all components organized by type",
            "/health": "Health check"
        },
        "supported_categories": CATEGORIES
    })


if __name__ == '__main__':
    app.run(debug=True)

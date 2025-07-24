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


        
@app.route('/components', methods=['GET'])
def get_comp():
    """Get components from OLX organized by category"""
    all_components = {cat: [] for cat in CATEGORIES}

    try:
        print("Starting to scrape OLX...")
        
        # Get data from OLX (returns flat list)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        data_olx = loop.run_until_complete(olxApi.main())
        loop.close()
        
        print(f"OLX returned {len(data_olx)} total items")
        
        
        # Merge into all_components
        for cat in CATEGORIES:
            all_components[cat].extend([item for item in data_olx if item['category'] == cat])
        
        # Show summary
        total_items = sum(len(items) for items in all_components.values())
        print(f"Total organized items: {total_items}")
        
        return jsonify(all_components)
        
    except Exception as e:
        print(f"Error in get_comp(): {e}")
        return jsonify({"error": f"Failed to scrape data: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "PC Build Scraper API is running"})

@app.route('/', methods=['GET'])
def home():
    """API documentation endpoint"""
    return jsonify({
        "message": "PC Build Scraper API",
        "endpoints": {
            "/components": "Get all components organized by type",
            "/health": "Health check"
        },
        "supported_categories": CATEGORIES
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.5000')

import time
from flask import Flask, jsonify, request
import asyncio
from typing import List, Dict, Any, Optional
import pikaConfiguration
from datetime import datetime

from offersScrapping import allegroApi
from offersScrapping import olxApi
from offersScrapping import allegroLokalneApi

app = Flask(__name__)

CATEGORIES = [
    "processor", "graphics_card", "ram", "case", "storage", "power_supply", "motherboard"
]


class ShopData:
    def __init__(self, name: str, components_data: List[Dict[str, Any]]):
        self.name = name
        self.components_data = components_data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "components_data": self.components_data,
        }


class ComponentData:
    def __init__(self, title: str, brand: str, model: str, price: float, url: str,
                 category: str, status: str, img: str):
        self.title = title
        self.brand = brand
        self.model = model
        self.price = price
        self.url = url
        self.category = category
        self.status = status
        self.img = img

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "brand": self.brand,
            "model": self.model,
            "price": self.price,
            "url": self.url,
            "category": self.category,
            "status": self.status,
            "img": self.img
        }


async def scrape_shop(shop_name: str) -> Optional[ShopData]:

    components_data = None
    started_at = datetime.now()

    try:
        print(f"Starting to scrape {shop_name}...")

        if shop_name == 'olx':
            components_data = await olxApi.main()
        elif shop_name == 'allegro':
            components_data = await allegroApi.main()
        elif shop_name == 'allegroLokalnie':
            components_data = await allegroLokalneApi.main()
        else:
            print(f"Unknown shop: {shop_name}")
            return None

        finished_at = datetime.now()
        execution_time = (finished_at - started_at).total_seconds()

        # Create ShopData object
        shop_data = ShopData(
            name=shop_name,
            components_data=components_data
        )

        print(f"{shop_name} returned {len(components_data)} total items in {execution_time:.2f}s")

        return shop_data

    except Exception as e:
        print(f"Error scraping {shop_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.route('/offers', methods=['POST'])
def get_offers():
    data = request.get_json()
    shops = data.get("shops", [])

    if not shops:
        return jsonify({
        }), 400

    # Validate shop names
    valid_shops = ["olx", "allegro", "allegroLokalne"]
    invalid_shops = [shop for shop in shops if shop not in valid_shops]
    if invalid_shops:
        return jsonify({
            "error": f"Invalid shop names: {invalid_shops}",
            "available_shops": valid_shops
        }), 400

    start_time = time.perf_counter()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Scrape all requested shops
        shop_data_list: List[ShopData] = []

        for shop in shops:
            shop_data = loop.run_until_complete(scrape_shop(shop))

            if shop_data is not None:
                shop_data_list.append(shop_data)

                # Send to RabbitMQ
                try:
                    print(shop_data.to_dict())
                    pikaConfiguration.send_to_rabbitmq("offers", shop_data.to_dict())
                except Exception as e:
                    print(f"Failed to send {shop} data to RabbitMQ: {e}")

        loop.close()

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Print summary
        print(f"\n{'=' * 60}")
        print(f"SCRAPING SUMMARY")
        print(f"{'=' * 60}")
        total_items = 0
        for shop_data in shop_data_list:
            items_count = len(shop_data.components_data)
            total_items += items_count
            shop_exec_time = (shop_data.finished_at - shop_data.started_at).total_seconds()
            print(f"{shop_data.name}: {items_count} items in {shop_exec_time:.2f}s")
        print(f"Total items: {total_items}")
        print(f"Total execution time: {execution_time:.2f} seconds ({execution_time / 60:.2f} minutes)")
        print(f"{'=' * 60}\n")
        return '', 204
    except Exception as e:
        print(f"Error in get_offers(): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to scrape data: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
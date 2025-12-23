import time
from flask import Flask, jsonify, request
import asyncio
from typing import List, Optional
from config import pikaConfiguration
from datetime import datetime
from model.dto_models import ComponentOfferDto, ScrapingOfferDto

from service import allegroApi, xkomApi
from service import olxApi
from service import allegroLokalnieApi

app = Flask(__name__)

VALID_SHOPS = ["olx", "allegro", "allegroLokalnie"]

async def scrape_shop(shop_name: str, update_id: Optional[int] = None) -> Optional[ScrapingOfferDto]:

    started_at = datetime.now()

    try:
        print(f"Starting to scrape {shop_name}...")

        components_data: List[ComponentOfferDto] = []
        
        if shop_name == 'olx':
            components_data = await olxApi.main()
        elif shop_name == 'allegro':
            components_data = await allegroApi.main()
        elif shop_name == 'allegroLokalnie':
            components_data = await allegroLokalnieApi.main()
        elif shop_name == 'x-kom':
            components_data = await xkomApi.main()
        else:
            print(f"Unknown shop: {shop_name}")
            return None

        finished_at = datetime.now()
        execution_time = (finished_at - started_at).total_seconds()

        if components_data and not isinstance(components_data[0], ComponentOfferDto):
            components_data = [
                ComponentOfferDto.from_dict(comp) if isinstance(comp, dict) else comp
                for comp in components_data
            ]

        shop_data = ScrapingOfferDto(
            updateId=update_id or 0,
            shopName=shop_name,
            componentsData=components_data
        )

        print(f"{shop_name} returned {len(components_data)} items in {execution_time:.2f}s")

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
        return jsonify({"error": "No shops specified"}), 400

    invalid_shops = [shop for shop in shops if shop not in VALID_SHOPS]
    if invalid_shops:
        return jsonify({
            "error": f"Invalid shop names: {invalid_shops}",
            "available_shops": VALID_SHOPS
        }), 400

    start_time = time.perf_counter()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        shop_data_list: List[ScrapingOfferDto] = []

        for shop in shops:
            shop_data = loop.run_until_complete(scrape_shop(shop))

            if shop_data is not None:
                shop_data_list.append(shop_data)

                try:
                    pikaConfiguration.send_to_rabbitmq("offers", shop_data.to_dict())
                except Exception as e:
                    print(f"Failed to send {shop} data to RabbitMQ: {e}")

        loop.close()

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Podsumowanie
        print(f"\n{'=' * 60}")
        print(f"SCRAPING SUMMARY")
        print(f"{'=' * 60}")
        total_items = sum(len(sd.componentsData) for sd in shop_data_list)
        for shop_data in shop_data_list:
            print(f"{shop_data.shopName}: {len(shop_data.componentsData)} items")
        print(f"Total items: {total_items}")
        print(f"Total execution time: {execution_time:.2f}s ({execution_time / 60:.2f}m)")
        print(f"{'=' * 60}\n")
        
        return '', 204
        
    except Exception as e:
        print(f"Error in get_offers(): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to scrape data: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
import asyncio
import threading
import json
import pika
from typing import Any

from offersScrapping import offer_controller
from bs4 import BeautifulSoup
import nodriver as uc

event_loop = asyncio.new_event_loop()
def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
threading.Thread(target=start_background_loop, args=(event_loop,), daemon=True).start()


def send_to_rabbitmq(queue_name: str, payload: Any):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    message = json.dumps(payload, default=str)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=1,
            content_type='application/json'
        )
    )
    connection.close()


async def check_offers_to_delete(offers_urls_list):
    offers_to_delete = []
    browser = await uc.start(headless=True)
    for url in offers_urls_list:
        try:
            page = await browser.get(url)
            html = await page.get_content()
            soup = BeautifulSoup(html, "html.parser")
            offer_title = soup.find("h4")
            if offer_title is not None:
                offers_to_delete.append(url)
        except Exception as e:
            print(f"Error while checking {url}: {e}")
    await browser.stop()
    return offers_to_delete



async def handle_scraping_task(update_id: int, shop: str):
    try:
        print(f"Starting scraping for {shop}, updateId={update_id}")
        shop_data = await offer_controller.scrape_shop(shop)

        if not shop_data:
            print(f"No data returned for shop {shop}")
            return

        result = shop_data.to_dict() if hasattr(shop_data, "to_dict") else dict(shop_data)

        payload = {
            "updateId": update_id,
            "shopName": shop,
            "componentsData": result.get("components_data", result.get("componentsData", [])),
        }

        send_to_rabbitmq(f"offersAdded.{shop}", payload)
        print(f"Sent offersAdded.{shop} for updateId={update_id}")

    except Exception as e:
        print(f"Error in handle_scraping_task for {shop}: {e}")


async def handle_check_task(update_id: int, shop: str, urls: list[str]):
    try:
        print(f"Checking offers for {shop}, urls={len(urls)}")
        offers_to_delete = await check_offers_to_delete(urls)

        payload = {
            "updateId": update_id,
            "shop": shop,
            "urls": offers_to_delete
        }

        send_to_rabbitmq(f"offersDeleted.{shop}", payload)
        print(f"Sent offersDeleted.{shop} with {len(offers_to_delete)} offers to delete")

    except Exception as e:
        print(f"Error in handle_check_task for {shop}: {e}")

def scrapping_callback(ch, method, properties, body):
    try:
        incoming = json.loads(body.decode("utf-8"))
        update_id = incoming.get("updateId")
        shop = incoming.get("shop")
        print(f"Received scraping task for {shop}, updateId={update_id}")

        asyncio.run_coroutine_threadsafe(handle_scraping_task(update_id, shop), event_loop)
    except Exception as e:
        print(f"Error in scrapping_callback: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def check_callback(ch, method, properties, body):
    try:
        incoming = json.loads(body.decode("utf-8"))
        update_id = incoming.get("updateId")
        shop = incoming.get("shop")
        urls = incoming.get("urls", [])
        print(f"Received check task for {shop}, updateId={update_id}, urls={len(urls)}")

        asyncio.run_coroutine_threadsafe(handle_check_task(update_id, shop, urls), event_loop)
    except Exception as e:
        print(f"Error in check_callback: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)



if __name__ == "__main__":
    SUPPORTED_SHOPS = ["olx", "allegro", "allegroLokalnie"]

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    for shop in SUPPORTED_SHOPS:
        print(f"Setting up queues for {shop}...")

        scraping_q = f"scrapingOffers.{shop}"
        check_q = f"checkOffers.{shop}"
        added_q = f"offersAdded.{shop}"
        deleted_q = f"offersDeleted.{shop}"

        for q in [scraping_q, check_q, added_q, deleted_q]:
            channel.queue_declare(queue=q, durable=True)

        channel.basic_consume(queue=scraping_q, on_message_callback=scrapping_callback)
        channel.basic_consume(queue=check_q, on_message_callback=check_callback)

    print("scraper started")
    channel.start_consuming()
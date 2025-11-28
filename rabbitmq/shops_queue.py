import re
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
import asyncio
import threading
import json
import traceback
import pika
from typing import List

from offersScrapping import offer_controller
from bs4 import BeautifulSoup
import nodriver as uc
from models.dto_models import ScrapingOfferDto

event_loop = asyncio.new_event_loop()

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_background_loop, args=(event_loop,), daemon=True).start()

SUPPORTED_SHOPS = ["olx", "allegro", "allegroLokalnie", "x-kom"]


def send_to_rabbitmq(queue_name: str, payload: dict):
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

async def check_offers_to_delete(offers_urls_list: List[str]) -> List[str]:
    offers_to_delete = []
    browser = None
    
    try:
        browser = await uc.start(headless=True)
        
        for url in offers_urls_list:
            try:
                page = await browser.get(url)

                for _ in range(4):
                    await page.evaluate("window.scrollBy(0, window.innerHeight);")
                    await asyncio.sleep(1)

                html = await page.get_content()
                soup = BeautifulSoup(html, "html.parser")
                is_expired = False
                
                if "olx.pl" in url:

                    expired = soup.find("h4", string=lambda t: "to ogłoszenie nie jest już dostępne" in t.lower() if t else False)
                    if expired:
                        is_expired = True

                elif "allegro.pl" in url and "lokalnie" not in url:

                    expired = soup.find("h6", string=lambda t: "sprzedaż zakończona" in t.lower() if t else False)
                    if expired:
                        is_expired = True

                elif "allegro.pl/lokalnie" in url or "allegrolokalnie.pl" in url:

                    el = soup.find("div", class_="mlc-offer-ended-banner")
                    if el:
                        is_expired = True

                    # if not el:
                    #     print("nie ", el)
                    #     el = soup.find("div", class_=re.compile(r"mlc-.*ended-banner"))

                if is_expired:
                    offers_to_delete.append(url)

            except Exception as e:
                print(f"Error while checking {url}: {e}")
                traceback.print_exc()
    
    except Exception as e:
        print(f"Error starting browser: {e}")
        traceback.print_exc()
    
    finally:
        if browser is not None:
            try:
                stop_result = browser.stop()
                if asyncio.iscoroutine(stop_result):
                    await stop_result
            except Exception as e:
                print(f"Error stopping browser: {e}")
    
    return offers_to_delete

async def handle_scraping_task(update_id: int, shop: str):
    try:
        print(f"Starting scraping for {shop}, updateId={update_id}")
        
        shop_data: ScrapingOfferDto = await offer_controller.scrape_shop(shop, update_id)

        if not shop_data:
            print(f"No data returned for shop {shop}")
            return

        send_to_rabbitmq(f"offersAdded.{shop}", shop_data.to_dict())
        print(f"Sent offersAdded.{shop} for updateId={update_id}, items={len(shop_data.componentsData)}")

    except Exception as e:
        print(f"Error in handle_scraping_task for {shop}: {e}")
        import traceback
        traceback.print_exc()


async def handle_check_task(update_id: int, shop: str, urls: List[str]):
    try:
        print(f"Checking offers for {shop}, urls={len(urls)}")
        
        if not urls or len(urls) == 0:
            print(f"No URLs to check for {shop}, sending empty result")
            payload = {
                "updateId": update_id,
                "shop": shop,
                "urls": []
            }
            send_to_rabbitmq(f"offersDeleted.{shop}", payload)
            return
        
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
        traceback.print_exc()

def scrapping_callback(ch, method, properties, body):
    try:
        incoming = json.loads(body.decode("utf-8"))
        update_id = incoming.get("updateId")
        shop = incoming.get("shop")
        print(f"Received scraping task for {shop}, updateId={update_id}")

        asyncio.run_coroutine_threadsafe(
            handle_scraping_task(update_id, shop), 
            event_loop
        )
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

        asyncio.run_coroutine_threadsafe(
            handle_check_task(update_id, shop, urls), 
            event_loop
        )
    except Exception as e:
        print(f"Error in check_callback: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
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

    print("Scraper started and listening...")
    channel.start_consuming()
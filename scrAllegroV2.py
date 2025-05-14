# pip3 install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup

# specify the API URL without the offset
target_url = "https://allegro.pl/kategoria/podzespoly-komputerowe-procesory-257222"

def scraper(url):

    # request the target website
    response = requests.get(url)

    # verify the response status
    if response.status_code != 200:
        return f"status failed with {response.status_code}"
    else:

        # parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # empty list to collect data
        scraped_data = []

        # get the product containers
        products = soup.find_all("div", class_="opbox-listing")

        # iterate through the product containers and extract the product content
        for product in products:
            name_tag = product.find(class_="mgn2_14 m9qz_yp mqu1_16 mp4t_0 m3h2_0 mryx_0 munh_0")
            price_tag = product.find(class_="mli8_k4 msa3_z4 mqu1_1 mp0t_ji m9qz_yo mgmw_qw mgn2_27 mgn2_30_s")

            data = {
                "name": name_tag.text if name_tag else "",
                "price": price_tag.text if price_tag else "",
            }

            # append the data to the empty list
            scraped_data.append(data)
        # return the scraped data
        return scraped_data

# execute the scraper function and print the scraped data
print(scraper(target_url))

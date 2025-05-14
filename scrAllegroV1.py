from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
# options.add_argument("--headless")  # bez okna przeglądarki
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0")

driver = webdriver.Chrome(options=options)
driver.get("https://allegro.pl")

time.sleep(5)  # poczekaj aż strona się załaduje

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

print(driver.page_source)

# soup = BeautifulSoup(driver.page_source, "html.parser")
# print(soup.prettify())


# Przykład: pobierz tytuły ofert
# for title in soup.select("h2.mgn2_14 m9qz_yp mqu1_16 mp4t_0 m3h2_0 mryx_0 munh_0")[:10]:
#     print(title.text.strip())

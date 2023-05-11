from bs4 import BeautifulSoup
from selenium import webdriver
import asyncio
from concurrent.futures import ThreadPoolExecutor
from forex_python.converter import CurrencyRates
from datetime import datetime, timedelta
import database


def scrape_amazon(url):
    options = webdriver.ChromeOptions()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/58.0.3029.110 Safari/537.3'
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return soup


def scrape_amazon_com(query):
    domain = f'https://www.amazon.com'
    url = f'{domain}/s?field-keywords={query}'
    soup = scrape_amazon(url)
    results = soup.select('.s-result-item')[:30]
    database.delete_all_search_results()

    for result in results:
        if database.check_10_rows():
            break

        try:
            name = result.select_one('.a-link-normal.a-text-normal').text
            link = domain + result.select_one('.a-link-normal.a-text-normal')['href']
            price_int = result.select_one('.a-price-whole').text
            price_frac = result.select_one('.a-price-fraction').text
            if None in [name, link, price_int, price_frac]:
                continue
            else:
                price = round(float(price_int + price_frac), 2)
                image = result.select_one('.s-image')['src']
                rating = result.select_one('.a-icon.a-icon-star-small').get_text(strip=True).split()[0]
                asin = result.get('data-asin')

                database.insert_item_search_results(query, name, link, price, image, rating, asin)

        except Exception as e:
            pass


def currency_rate(from_currency):
    c = CurrencyRates()
    conv_date = datetime.now()
    while True:
        try:
            ex_rate = c.get_rate(from_currency, 'USD', conv_date)
            return ex_rate
        except Exception as e:
            conv_date -= timedelta(days=1)


CONV_RATE = {"ca": currency_rate("CAD"),
             "de": currency_rate("EUR"),
             "co.uk": currency_rate("GBP")}


def scrape_amazon_other(identifier, row_id, by_asin=True):
    # get asin or name
    search_result = database.get_row_by_pk_search_results(row_id)
    asin = search_result.ASIN
    name = search_result.Name

    domain = f'https://www.amazon.{identifier}'
    url = f'{domain}/s?field-keywords={asin if by_asin else name}'
    soup = scrape_amazon(url)
    results = soup.select('.s-result-item')[:10]

    for result in results:
        try:
            curr_asin = result.get('data-asin')

            if by_asin:
                found_item = (curr_asin == asin)
            else:
                found_item = (result.select_one('.a-link-normal.a-text-normal').text == name)

            if found_item:
                link = domain + result.select_one('.a-link-normal.a-text-normal')['href']
                price = result.select_one('.a-price-whole').text + result.select_one('.a-price-fraction').text
                price = round(float(price) * CONV_RATE[identifier], 2)
                database.update_item_search_results(name, identifier, price, link)
                break

        except Exception as e:
            pass


async def async_scrape_amazon(row_id, by_asin=True, other_amazons=("ca", "co.uk", "de")):
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [loop.run_in_executor(executor, scrape_amazon_other, other_amazon, row_id, by_asin)
                 for other_amazon in other_amazons]

    results = await asyncio.gather(*tasks)
    return results



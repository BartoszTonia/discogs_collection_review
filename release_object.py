from datetime import datetime
from time import time, sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import logging
import re

logger = logging.getLogger(__name__)

timeout = 8
options = Options()
options.add_argument('headless')
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option('excludeSwitches', ['enable-logging'])


def run_driver(url):
    print('>>> ', end='')
    service = Service("driver\chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service)
    delay = 3  # seconds
    try:
        driver.get(url)
    except WebDriverException as e:
        if "net::ERR_CONNECTION_TIMED_OUT" in str(e):
            print("Error: Connection timed out.")
        else:
            # This will handle other WebDriverException errors that aren't specifically a timeout.
            print\
                (f"WebDriver error occurred: {e}")
        quit()
    except KeyboardInterrupt:
        print('Ctrl+C......')
        quit()
    except Exception as e:
        # This is a generic exception handler.
        print(f"An unexpected error occurred: {e}")
        quit()

    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, Selector().sale)))
    except TimeoutException:
        print('<<<')
        sleep(10)
        pass

    return driver


table_selector = '#page > div > div:nth-child(2) > div > div.info_23nnx > '


class Selector:
    def __init__(self):
        self.start = '.price_2Wkos'
        self.low = '.items_3gMeU > ul:nth-child(2) > li:nth-child(2) > span:nth-child(2)'
        self.med = '.items_3gMeU > ul:nth-child(2) > li:nth-child(3) > span:nth-child(2)'
        self.high = '.items_3gMeU > ul:nth-child(2) > li:nth-child(4) > span:nth-child(2)'
        self.last = '.items_3gMeU > ul:nth-child(2) > li:nth-child(1) > a:nth-child(2) > time:nth-child(1)'
        self.want = '#release-stats > div > div > ul:nth-child(1) > li:nth-child(2) > a'
        self.have = '#release-stats > div > div > ul:nth-child(1) > li:nth-child(1) > a'
        self.label_and_catalog = table_selector + 'table > tbody > tr:nth-child(1) > td'
        self.media_format = table_selector + 'table > tbody > tr:nth-child(2) > td'
        self.date = table_selector + 'table > tbody > tr:nth-child(4) > td > a > time'
        self.sale = '.forsale_QoVFl > a:nth-child(1)'
        self.avg_rate = '#release-stats > div > div > ul:nth-child(1) > li:nth-child(3) > span:nth-child(2)'
        self.rate_count = '#release-stats > div > div > ul:nth-child(1) > li:nth-child(4) > a'
        self.ships = '.marketplace_aside > div:nth-child(3) > div:nth-child(2) > p:nth-child(5)'

        # Alternative CSS selectors if "Series" appears in the table
        self.has_series = table_selector + 'table > tbody > tr:nth-child(2) > th'
        self.media_format_alt = table_selector + 'table > tbody > tr:nth-child(3) > td'
        self.date_alt = table_selector + 'table > tbody > tr:nth-child(5) > td > a > time'


class Pattern:
    def __init__(self):
        self.price = r'(?:[$£¥€])(\d*.\d\d)'
        self.sale = r'(\d*)'
        self.avg = r"(\d+(?:\.\d+)?)<!-- --> / 5"
        self.ships = r'(?<=>Item Ships From:</strong>\s)(\w+\s*\w+\s*)'
        self.ship_cost = r'(?:[$£¥€])(\d+.\d+)\s(?:shipping)'


class ReleaseObject:
    def __init__(self, release_id, title):
        self.id = release_id
        self.url = 'https://www.discogs.com/release/' + str(self.id)
        self.select, self.pattern = Selector(), Pattern()
        self.driver = run_driver(self.url)
        self.title = title
        self.want = self.get_data(self.select.want)
        self.have = self.get_data(self.select.have)

        self.start = self.get_price(self.select.start)
        self.low = self.get_price(self.select.low)
        self.med = self.get_price(self.select.med)
        self.high = self.get_price(self.select.high)

        self.for_sale = self.get_data(self.select.sale, self.pattern.sale)
        self.avg_rating = self.get_data(self.select.avg_rate, self.pattern.avg)
        self.rating_count = self.get_data(self.select.rate_count)
        self.last_sold = self.get_data(self.select.last)
        self.date_of_scrape = self.get_timestamp()
        self.styles = self.get_styles()
        self.label, self.cat = self.get_label_and_catalog()

        self.format = self.extract_format_details()
        self.date_of_release = self.get_datetime()
        self.driver.quit()

    def get_data(self, select, pattern=None):
        try:
            data = self.driver.find_element(By.CSS_SELECTOR, select).get_attribute('innerHTML')
            if pattern:
                data = self.get_data(select)
                return re.findall(pattern, str(data), re.DOTALL)[0]
            else:
                return data
        except (IndexError, NoSuchElementException):
            print(self.driver.current_url, 'err', select, pattern)
            print(self.driver.title)
            return 0

    def get_styles(self):
        """
        Retrieves a list of styles available for the release from the release page.

        Returns:
        list or string: A list of available styles descriptions for the release.
        """
        try:
            styles_pattern = r'"styles":\[(.*?)\]'
            styles_match = re.search(styles_pattern, self.driver.page_source, re.DOTALL)

            if styles_match:
                styles_raw = styles_match.group(1)
                # Split the styles and remove unnecessary quotes and spaces
                styles_list = [s.strip(' " ') for s in styles_raw.split(',')]
                # Join the cleaned styles with '/'
                return ' / '.join(styles_list)
            else:
                return ''
        except Exception as e:
            logger.error(f' > get_styles function: {e} at {self.url}')
            return ''

    def get_label_and_catalog(self):
        try:
            td_element = self.driver.find_element(By.CSS_SELECTOR, self.select.label_and_catalog)

            # Extract label
            label = td_element.find_element(By.TAG_NAME, 'a').text.strip()

            # Extract catalogue number
            catalog_text = td_element.text.strip()
            catalog_number = catalog_text.replace(label, '').strip(' "–').lstrip()

            return label, catalog_number
        except NoSuchElementException as e:
            logger.error(f' > get_label_and_catalog function: {e} at {self.url}')
            return None, None

    def has_series(self):
        try:
            table_content = self.driver.find_element(By.CSS_SELECTOR, self.select.has_series).text
            if "Series" in table_content:
                return True
            else:
                return False
        except NoSuchElementException:
            return False

    def extract_format_details(self):
        try:
            # Select all containers of the format details
            if self.has_series():
                containers = self.driver.find_elements(By.CSS_SELECTOR, self.select.media_format_alt)
            else:
                containers = self.driver.find_elements(By.CSS_SELECTOR, self.select.media_format)

            # Set for primary formats like Vinyl, Memory Stick, etc.
            format_types = set()
            # Set for additional attributes like Limited Edition, 33 ⅓ RPM, etc.
            attributes = set()

            for container in containers:
                # Extract the anchor tag content (the format type)
                a_tag = container.find_element(By.TAG_NAME, 'a')
                link_text = a_tag.text.strip()

                # Add primary format type to set if not already present
                if link_text not in format_types:
                    format_types.add(link_text)

                # Extract the full text of the container and remove the anchor tag's text
                full_text = container.text.strip().replace('\n', ' ')  # Replace internal line breaks with a space
                remaining_text = full_text.replace(link_text, '', 1).strip()

                # Split the remaining text by commas and add each keyword to the attributes set
                for keyword in remaining_text.split(','):
                    cleaned_keyword = keyword.strip()
                    if cleaned_keyword and cleaned_keyword not in attributes:
                        attributes.add(cleaned_keyword)

            # Create final output
            return ' '.join(list(format_types) + list(attributes))

        except Exception as e:
            logger.error(f"Error extracting format: {e} at {self.url}")
            return None

    def get_datetime(self):
        try:
            if self.has_series():
                time_element = self.driver.find_element(By.CSS_SELECTOR, self.select.date_alt)
            else:
                time_element = self.driver.find_element(By.CSS_SELECTOR, self.select.date)

            # Extract datetime attribute
            datetime_value = time_element.get_attribute('datetime').strip()
            return datetime_value
        except NoSuchElementException as e:
            logger.error(f' > get_datetime function: {e} at {self.url}')
            return None

    @staticmethod
    def get_timestamp():
        t = time()
        timestamp = datetime.fromtimestamp(t).strftime('%Y%m%d_%H_%M')
        return timestamp

    def get_price(self, select):
        data = self.get_data(select)
        price, currency = self.currency_check(data)
        price = re.findall(self.pattern.price, price, re.DOTALL)
        price = self.convert_float(price, currency)
        return price

    @staticmethod
    def convert_float(price, currency):
        try:
            price = float(price[0])
            return round(price * currency, 2)
        except ValueError:
            price = float(re.sub(",", "", str(price[0])))
            price *= 10
            return round(price * currency, 2)
        except IndexError:
            return 0

    @staticmethod
    def currency_check(price):
        funt_eur = 1.17
        dollar_eur = 0.84
        yen_eur = 0.0077
        try:
            if '£' in price: return price, funt_eur
            elif '¥' in price: return price, yen_eur
            elif '$' in price: return price, dollar_eur
            else:
                return price, 1
        except TypeError:
            return '€0.00', 1

    def csv_object(self):
        """
        Returns a tuple of data that can be written as a line to a CSV file.
        """
        columns = (self.id, self.title, self.for_sale, self.start,
                   self.low, self.med, self.high, self.avg_rating, self.rating_count,
                   self.want, self.have, self.last_sold, self.styles,
                   self.date_of_release, self.date_of_scrape, self.url, self.label, self.cat, self.format)
        return columns

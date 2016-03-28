import string

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


class GoogleEarningDateScraper(object):
    google_finance_url_part = 'https://www.google.com/finance?q='

    def __init__(self, thread_waiting_seconds):
        self.waiting_seconds = thread_waiting_seconds

    def fetch_earning_date(self, stock):
        request_url = self.google_finance_url_part + stock
        driver = webdriver.Firefox()
        driver.implicitly_wait(self.waiting_seconds)
        driver.get(request_url)

        event_div = driver.find_element_by_class_name('events')

        inner_text = event_div.text
        driver.close()

        extracted_earn_date = GoogleEarningDateScraper._extract_html(inner_text)
        return extracted_earn_date

    def fetch_bulk_earning_date(self, stock_list):
        earn_date_data = []
        driver = webdriver.Firefox()
        driver.implicitly_wait(self.waiting_seconds)

        for stock in stock_list:
            request_url = self.google_finance_url_part + stock
            driver.get(request_url)
            event_div = driver.find_element_by_class_name('events')
            inner_text = event_div.text
            extracted_earn_date = GoogleEarningDateScraper._extract_html(inner_text)
            earn_date_data.append(extracted_earn_date)

        driver.close()
        return earn_date_data

    @staticmethod
    def _extract_html(html_to_extract):
        inner_text = html_to_extract.split('\n')
        for index in range(len(inner_text)):
            if('Earnings Call' in inner_text[index]):
                return inner_text[index - 1]
        return ''

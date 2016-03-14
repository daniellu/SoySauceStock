import logging
import requests
import pandas as pd
from lxml import html

logger = logging.getLogger(__name__)


class StockChartScraper(object):

    stock_chart_url = 'https://stockcharts.com/scripts/php/dblogin.php'

    def __init__(self, stock_list, login_config, multi_thread=True):
        self.stock_list = stock_list
        self.multi_thread = multi_thread
        self.login_config = login_config

    def login_stock_chart_site(self):
        s = requests.Session()
        s.post(StockChartScraper.stock_chart_url, data=self.login_config)
        return s

    def fetch_stock_html_table(self, logined_session, stock_html):
        page = logined_session.get(stock_html)
        tree = html.fromstring(page.content)
        price_table_part = tree.xpath('//div[@id="historic-data-body"]/pre/text()')
        logined_session.close()
        return price_table_part[0]

    def parse_data_frame_from_html_table(self, html_table):
        table_lines = html_table.splitlines()
        # we only want data after the first 3 rows, split data into array of array
        line_array = [tableRow.split()[1:] for tableRow in filter(None, table_lines[3:])]

        data_frame_from_record = pd.DataFrame.from_records(line_array,
                                                           columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        data_frame_from_record['Date'] = pd.to_datetime(data_frame_from_record['Date'])
        data_frame_from_record.sort_index(ascending=True, axis=1)
        return data_frame_from_record

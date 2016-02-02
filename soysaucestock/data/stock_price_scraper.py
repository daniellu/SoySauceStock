import logging
import requests
import os
from lxml import html

logger = logging.getLogger(__name__)
stock_chart_url = 'https://stockcharts.com/scripts/php/dblogin.php'


def get_stock_chart_login_from_config():
    return {'form_UserID': 'boyuhou@gmail.com', 'form_UserPassword': 'thisisatest'}


class StockChartScraper(object):
    def __init__(self, stock_list, login_config, multi_thread=True):
        self.stock_list = stock_list
        self.multi_thread = multi_thread

        if login_config is None:
            login_config = get_stock_chart_login_from_config()
        self.login_config = login_config

    def login_stock_chart_site(stock_chart_login):
        s = requests.Session()
        s.post(stock_chart_url, data=stock_chart_login)
        return s

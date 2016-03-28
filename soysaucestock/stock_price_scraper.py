import requests
import pandas as pd
import json
import os
from lxml import html


class StockChartScraper(object):

    stock_chart_login_url = 'https://stockcharts.com/scripts/php/dblogin.php'
    stock_chart_data_url = 'http://stockcharts.com/h-hd/?'

    def __init__(self):
        pass

    @staticmethod
    def _login_stock_chart_site(login_config_path):
        with open(login_config_path) as json_file:
            config = json.load(json_file)
        login_config = {'form_UserID': config['user_name'], 'form_UserPassword': config['password']}
        s = requests.Session()
        s.post(StockChartScraper.stock_chart_login_url, data=login_config)
        return s

    @staticmethod
    def save_stocks(stock_list, dest='C:\\temp', login_config_path='C:\\Tools\\stockchart.json', is_lazy_save=True):
        if type(stock_list) is not list:
            stock_list = [stock_list]

        s = StockChartScraper._login_stock_chart_site(login_config_path)
        for index in range(0, len(stock_list)):
            ticker = stock_list[index].replace('/', '%2F')
            file_dest = os.path.join(dest, str.format('{0}.csv', stock_list[index].replace('/', '.')))
            if is_lazy_save and os.path.isfile(file_dest):
                pass
            else:
                StockChartScraper._save_stock(s, ticker, file_dest)

    @staticmethod
    def _save_stock(s,ticker, file_dest):
        html_table = StockChartScraper._fetch_stock_html_table(s, ticker)
        df = StockChartScraper._parse_data_frame_from_html_table(html_table)
        df.to_csv(file_dest, index=False, header=True)

    @staticmethod
    def _fetch_stock_html_table(login_session, ticker):
        page = login_session.get(StockChartScraper.stock_chart_data_url + ticker)
        tree = html.fromstring(page.content)
        price_table_part = tree.xpath('//div[@id="historic-data-body"]/pre/text()')
        return price_table_part[0]

    @staticmethod
    def _parse_data_frame_from_html_table(html_table):
        table_lines = html_table.splitlines()
        # we only want data after the first 3 rows, split data into array of array
        line_array = [tableRow.split()[1:] for tableRow in filter(None, table_lines[3:])]

        data_frame_from_record = pd.DataFrame.from_records(line_array,
                                                           columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        data_frame_from_record['Date'] = pd.to_datetime(data_frame_from_record['Date'])
        data_frame_from_record = data_frame_from_record.sort_index(ascending=False, axis=0)
        return data_frame_from_record

from lxml import html
import time
import requests
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import pandas as pd
import csv
import stock_price_scraper

url = 'https://stockcharts.com/scripts/php/dblogin.php'
stockchartlogin = {'form_UserID': 'YOUR_USERNAME@gmail.com', 'form_UserPassword': 'YOUR_PASSWORD'}


if __name__ == '__main__':

    scraper = stock_price_scraper.StockChartScraper(stock_list=[], login_config=stockchartlogin)
    session = scraper.login_stock_chart_site()
    table_content = scraper.fetch_stock_html_table(session,'http://stockcharts.com/h-hd/?RY.TO')
    dataFrameFromRecord = scraper.parse_data_frame_from_html_table(table_content)

    io = StringIO(table_content)
    f = open('data.csv', 'wt')

    try:
        writer = csv.writer(f)
        i = 0
        for line in io:
            i += 1
            if i not in [1, 3]:
                line = line.split()
                writer.writerow(line[1:len(line)])

    finally:
        f.close()
    df = pd.DataFrame.from_csv('data.csv', sep=",", parse_dates=True)


	#save both data frames to csv to validate if the data is correct, data identified
    dataFrameFromRecord.to_csv('dataFromMemory.csv', index=False)
    df.to_csv('df_FromCSV.csv')

    #store = pd.HDFStore('data.h5')
    #store['price/RY_TO'] = df
    #store.close()
    #ry = pd.read_hdf('data.h5', 'price/RY_TO')

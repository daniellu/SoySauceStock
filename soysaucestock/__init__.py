try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import pandas as pd
import csv
import stock_price_scraper
import argparse
import json
import os

url = 'https://stockcharts.com/scripts/php/dblogin.php'

# run param  --config C:\Tools\stockchart.json --dest C:\temp
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='StockChart Parser')
    parser.add_argument('--config', type=argparse.FileType('r'), help="Path to the login file.", required=True)
    parser.add_argument('--dest', help="Path to save file.", required=True)

    args = parser.parse_args()
    config = json.load(args.config)
    user_name = config['user_name']
    password = config['password']
    target_path = args.dest
    stockchartlogin = {'form_UserID': config['user_name'], 'form_UserPassword': config['password']}

    scraper = stock_price_scraper.StockChartScraper(stock_list=[], login_config=stockchartlogin)
    session = scraper.login_stock_chart_site()
    table_content = scraper.fetch_stock_html_table(session,'http://stockcharts.com/h-hd/?%24TSX')   #TSX data
    dataFrameFromRecord = scraper.parse_data_frame_from_html_table(table_content)

    # io = StringIO(table_content)
    # f = open('data.csv', 'wt')
    #
    # try:
    #     writer = csv.writer(f)
    #     i = 0
    #     for line in io:
    #         i += 1
    #         if i not in [1, 3]:
    #             line = line.split()
    #             writer.writerow(line[1:len(line)])
    #
    # finally:
    #     f.close()
    # df = pd.DataFrame.from_csv('data.csv', sep=",", parse_dates=True)


	#save both data frames to csv to validate if the data is correct, data identified
    dataFrameFromRecord.to_csv(os.path.join(target_path, 'dataFromMemory.csv'), index=True, header=False)
    # df.to_csv('df_FromCSV.csv')

    #store = pd.HDFStore('data.h5')
    #store['price/RY_TO'] = df
    #store.close()
    #ry = pd.read_hdf('data.h5', 'price/RY_TO')

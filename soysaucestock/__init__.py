from lxml import html
import time
import requests
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import pandas as pd
import csv

url = 'https://stockcharts.com/scripts/php/dblogin.php'
stockchartlogin = {'form_UserID': 'YOUR_USERNAME@gmail.com', 'form_UserPassword': 'YOUR_PASSWORD'}

if __name__ == '__main__':
    s = requests.Session()
    s.post(url, data=stockchartlogin)
    page = s.get('http://stockcharts.com/h-hd/?RY.TO')
    tree = html.fromstring(page.content)
    priceTablePart = tree.xpath('//div[@id="historic-data-body"]/pre/text()')
    s.close()

    tableLines = priceTablePart[0].splitlines()
    #we only want data after the first 3 rows, split data into array of array
    lineArray = [tableRow.split()[1:] for tableRow in filter(None, tableLines[3:])]

    dataFrameFromRecord = pd.DataFrame.from_records(lineArray, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    dataFrameFromRecord.sort_index(ascending=True, axis=1)

    io = StringIO(priceTablePart[0])
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

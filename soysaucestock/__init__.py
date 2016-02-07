from lxml import html
import requests
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import pandas as pd
import csv

url = 'https://stockcharts.com/scripts/php/dblogin.php'
stockchartlogin = {'form_UserID':'boyuhou@gmail.com','form_UserPassword':'thisisatest'}

if __name__ == '__main__':
    s = requests.Session()
    s.post(url, data=stockchartlogin)
    page = s.get('http://stockcharts.com/h-hd/?RY.TO')
    tree = html.fromstring(page.content)
    priceTablePart = tree.xpath('//div[@id="historic-data-body"]/pre/text()')
    s.close()

	tableLines = priceTablePart[0].splitlines()
	#we only want data after the first 3 rows, splict data into array of array
    lineArray = []
    index = 0;
    for tableRow in tableLines:
        index += 1
        if index not in [1, 3]:
            cells = tableRow.split()[1:]
            lineArray.append(cells)
    print(lineArray[0])
    dataFrameFromRecord = pd.DataFrame.from_records(lineArray)
    dataFrameFromRecord.sort_index(ascending=True, axis=0)

    store = pd.HDFStore('data.h5')
    store['price/RY_TO'] = dataFrameFromRecord
    store.close()
    #ry = pd.read_hdf('data.h5', 'price/RY_TO')

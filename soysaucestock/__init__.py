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
    a = tree.xpath('//div[@id="historic-data-body"]/pre/text()')
    s.close()

    io = StringIO(a[0])
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
    df = df.sort_index(ascending=True, axis=0)

    store = pd.HDFStore('data.h5')
    store['price/RY_TO'] = df
    store.close()
    #ry = pd.read_hdf('data.h5', 'price/RY_TO')

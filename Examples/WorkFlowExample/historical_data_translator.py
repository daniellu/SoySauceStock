__author__ = 'zlu'
from datetime import datetime


class HistoricalDataTranslator(object):
    browser_time = datetime(year=1970, month=1, day=1)

    # This method is going to translate the .net data into
    # the python data structure
    # for now I would just show how to iterate the .net list
    # and translate to array for the graph
    # Bryan would probably use Pandas here
    @staticmethod
    def translate(data_from_net):
        tranlate_result = []
        for i in range(0, data_from_net.Length):
            tranlate_result.append(HistoricalDataTranslator.translate_single_point(data_from_net[i]))
        return tranlate_result

    @staticmethod
    def translate_single_point(point):
        return [HistoricalDataTranslator.date_string_to_browser_milliseconds(point.Date), point.Open, point.High,
                point.Low, point.Close, point.Volume]

    # sample date time: 20130904  12:57:00
    # format mask: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    @staticmethod
    def date_string_to_browser_milliseconds(date_string):
        datetime_object = datetime.strptime(date_string, '%Y%m%d %H:%M:%S')
        seconds = (datetime_object - HistoricalDataTranslator.browser_time).total_seconds()
        milli_seconds = int(seconds * 1000.0)
        return milli_seconds

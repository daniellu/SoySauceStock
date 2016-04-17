import graph_html_generator
from historical_data_translator import HistoricalDataTranslator
import sys
sys.path.append(r"C:\Users\Daniel\Desktop\Examples\WorkFlowExample\Dlls")
import clr
clr.AddReference(r"DynamicFetcher")

from DynamicFetcher import DataFetcher

if __name__ == '__main__':
    template_folder = r'C:\Users\Daniel\Desktop\Examples\WorkFlowExample'
    template_name = 'Chart-template.html'
    export_path = r'C:\Users\Daniel\Desktop\Examples\WorkFlowExample\Result\test123.html'
    fetcher = DataFetcher()
    result = fetcher.__class__.__name__
    print('.NET Class name: ' + result)
    greetingResult = fetcher.Greeting('Hello World!')
    print('Validation message from .NET:' + greetingResult)

    data = fetcher.History('TRI', '20131015 06:00:00', '10 D', '1 min')
    print('Received historical data from TWS...')

    # translate the data into pndas here
    translate_data = HistoricalDataTranslator.translate(data)

    generator = graph_html_generator.GraphHtmlGenerator(template_folder=template_folder,
                                                        template_name=template_name)
    generator.generate_html(stock_data=translate_data, export_path=export_path)


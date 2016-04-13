import google_earningdate_scraper
import yahoo_earningdate_scraper
import graph_html_generator
import webbrowser
import os

if __name__ == '__main__':
    test_data = [[1239667200000,17.08,17.17,16.75,16.90,113688925],[1239753600000,16.74,16.89,16.54,16.81,103256790],[1239840000000,17.03,17.59,16.97,17.35,148395562]];

    generator = graph_html_generator.GraphHtmlGenerator(template_folder=r'E:\Python\Study',
                                                        template_name='Chart-template.html')
    generator.generate_html(stock_data=test_data, export_path=r'E:\Python\Study\Result\test123.html')


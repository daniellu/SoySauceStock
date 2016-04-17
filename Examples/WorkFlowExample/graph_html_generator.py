__author__ = 'zlu'

from jinja2 import Environment, FileSystemLoader
import os
import webbrowser


class GraphHtmlGenerator(object):
    template_path = ''

    def __init__(self, template_folder, template_name):
        self.template_folder = template_folder
        self.template_name = template_name

    def generate_html(self, stock_data, export_path):
        # Create the jinja2 environment.
        # Notice the use of trim_blocks, which greatly helps control whitespace.
        env = Environment(loader=FileSystemLoader(self.template_folder), trim_blocks=True)
        template = env.get_template(self.template_name)

        data_html_part = GraphHtmlGenerator._generate_data_html(stock_data)
        result_html = template.render(PRICE_DATA=data_html_part)
        GraphHtmlGenerator._save_html(export_path, result_html)
        webbrowser.open('file://' + os.path.realpath(export_path))

    @staticmethod
    def _save_html(file_name, result_html):
        with open(file_name, "w") as text_file:
            text_file.write(result_html)

    @staticmethod
    def _generate_data_html(data_array):
        data_html = '['
        for row in data_array:
            row_html = '[{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]}],'.format(r=row)
            data_html += row_html

        data_html += ']'
        return data_html

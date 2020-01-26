from typing import List

import jinja2

from .config import ConfigParser, AppConfig, TableConfig
from .db import DBManager, QueryBuilder


class RowData:

    def __init__(self, headers: List[str]):
        self.data: List[tuple] = []
        self.headers: List[str] = headers

    def add(self, row: tuple):
        self.data.append(row)


class Report:
    TEMPLATE_FILE = 'template.html'

    def __init__(self, row_data: RowData):
        self.row_data = row_data

    def _load_template(self):
        template_loader = jinja2.FileSystemLoader(searchpath="./resources")
        template_env = jinja2.Environment(loader=template_loader)
        return template_env.get_template(self.TEMPLATE_FILE)

    def render(self) -> str:
        template = self._load_template()
        return template.render(header=self.row_data.headers, data=self.row_data.data)


class App:
    INPUT_CONFIG_FILE = 'INPUT_CONFIG_FILE'
    INPUT_TABLE = 'INPUT_TABLE'
    OUTPUT_FILE = 'OUTPUT_FILE'

    def __init__(self, args):
        config: ConfigParser = ConfigParser(args[self.INPUT_CONFIG_FILE])
        self.input_table: str = args[self.INPUT_TABLE]
        self.output_file: str = args[self.OUTPUT_FILE]
        self.app_config: AppConfig = config.app_config
        self.table_config: TableConfig = config.relation(self.input_table)
        self.db_manager = DBManager(self.app_config.db_config)

    def run(self):
        columns = self.db_manager.sql_field_names(self.table_config.src_relation)
        sql = QueryBuilder(self.table_config, columns).build('t0', 't1')
        cur = self.db_manager.query(sql)
        row_data = RowData(columns)
        for x in cur:
            row_data.add(x)
        report = Report(row_data)
        with open(self.output_file, 'w') as f:
            f.write(report.render())

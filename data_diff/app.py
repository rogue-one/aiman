from os import path
from typing import List

import jinja2

from .config import ConfigParser, AppConfig, TableConfig
from .db import DBManager, QueryBuilder, RelationFields


class RowData:

    def __init__(self, headers: RelationFields):
        self.data: List[tuple] = []
        self.headers: RelationFields = headers

    def add(self, row: tuple):
        filter(lambda x: x[0] < len(self.headers.keys), row)
        key_data = [x for (idx, x) in enumerate(row) if idx < len(self.headers.keys)]
        col_data = [x for (idx, x) in enumerate(row) if idx >= len(self.headers.keys)]
        data = (key_data, zip(*(iter(col_data),) * 2))
        self.data.append(data)


class Report:
    TEMPLATE_FILE = 'template.html'

    def __init__(self,
                 report_name: str,
                 row_data: RowData):
        self.report_name = report_name
        self.row_data = row_data

    def _load_template(self):
        template_loader = jinja2.FileSystemLoader(searchpath=path.dirname(__file__))
        template_env = jinja2.Environment(loader=template_loader)
        return template_env.get_template(self.TEMPLATE_FILE)

    def render(self) -> str:
        template = self._load_template()
        return template.render(report=self.report_name,
                               keys=self.row_data.headers.keys,
                               cols=self.row_data.headers.columns,
                               data=self.row_data.data)


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
        columns = self.db_manager.sql_field_names(self.table_config.src_relation, self.table_config.keys)
        sql = QueryBuilder(self.table_config, columns).build('t0', 't1')
        cur = self.db_manager.query(sql, self.app_config.max_rows)
        row_data = RowData(columns)
        for x in cur:
            row_data.add(x)
        report = Report(self.table_config.name, row_data)
        with open(self.output_file, 'w') as f:
            f.write(report.render())

    def _fetch_columns(self):
        columns = self.db_manager.sql_field_names(self.table_config.src_relation, self.table_config.keys)
        for x in self.table_config.keys:
            assert x in columns, 'key column %s not found in the relation' % x

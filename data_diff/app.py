from os import path
from typing import List

import jinja2

from .config import ConfigParser, AppConfig, TableConfig
from .db import DBManager, QueryBuilder, RelationFields


class RowData:
    """
    A container class that holds the header and diff data from the sql query.
    This will segregate the headers into key columns and normal columns.
    similarly the data also segregated into key field data and other fields data from source and target sqls.
    """
    def __init__(self, headers: RelationFields):
        self.data: List[tuple] = []
        self.headers: RelationFields = headers

    def add(self, row: tuple):
        """
        add a single row from sql query
        :param row:
        :return:
        """
        filter(lambda x: x[0] < len(self.headers.keys), row)
        key_data = [x for (idx, x) in enumerate(row) if idx < len(self.headers.keys)]
        col_data = [x for (idx, x) in enumerate(row) if idx >= len(self.headers.keys)]
        data = (key_data, zip(*(iter(col_data),) * 2))
        self.data.append(data)


class Report:
    """
    Generate HTML report
    """
    TEMPLATE_FILE = 'template.html'

    def __init__(self,
                 report_name: str,
                 row_data: RowData):
        self.report_name = report_name
        self.row_data = row_data

    def _load_template(self):
        """
        load template from file system.
        :return:
        """
        template_loader = jinja2.FileSystemLoader(searchpath=path.dirname(__file__))
        template_env = jinja2.Environment(loader=template_loader)
        return template_env.get_template(self.TEMPLATE_FILE)

    def render(self) -> str:
        """
        render the template with valid values.
        :return:
        """
        template = self._load_template()
        return template.render(report=self.report_name,
                               keys=self.row_data.headers.keys,
                               cols=self.row_data.headers.columns,
                               data=self.row_data.data)


class App:
    """
    Main application
    """
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
        """
        execute data diff application
        :return:
        """
        columns = self.db_manager.sql_field_names(self.table_config.src_relation, self.table_config.keys)
        sql = QueryBuilder(self.table_config, columns).build('t0', 't1')
        row_data = self._execute_sql(columns, sql)
        self._create_report(row_data)

    def _execute_sql(self,
                     columns: RelationFields,
                     sql: str) -> RowData:
        """
        execute query and make RowData
        :param columns:
        :param sql:
        :return:
        """
        print(
            """
            {t_border}
            {sql}
            {b_border}
            """.format(t_border='=' * 100, b_border='=' * 100, sql=sql)
        )
        cur = self.db_manager.query(sql, self.app_config.max_rows)
        row_data = RowData(columns)
        for x in cur:
            row_data.add(x)
        return row_data

    def _create_report(self, row_data: RowData):
        """
        create report and write to html file
        :param row_data:
        :return:
        """
        report = Report(self.table_config.name, row_data)
        with open(self.output_file, 'w') as f:
            f.write(report.render())

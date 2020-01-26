from typing import List

import psycopg2

from config import DBConfig, TableConfig


class CursorWrapper:
    """
    a generator that wraps around the cursor and closes it once all data has been exhausted by the consumer.
    """

    def __init__(self, cursor):
        self._cursor = cursor

    def __iter__(self):
        for row in self._cursor:
            yield row
        try:
            self._cursor.close()
        except _:
            pass


class DBManager:

    def __init__(self, db_config: DBConfig):
        self.db_config: DBConfig = db_config
        self._conn = DBManager._create_connection(db_config)

    @staticmethod
    def _create_connection(conf: DBConfig):
        return psycopg2.connect(
            host=conf.hostname,
            user=conf.username,
            password=conf.password,
            port=conf.port,
            database=conf.default_db
        )

    def sql_field_names(self, sql: str) -> List[str]:
        query: str = "SELECT * FROM (%s) t0 WHERE 1 = 0" % sql
        cursor = self._conn.cursor()
        cursor.execute(query)
        return [x.name for x in cursor.description]

    def query(self, sql) -> CursorWrapper:
        cursor = self._conn.cursor()
        cursor.execute(sql)
        return CursorWrapper(cursor)

    def shutdown(self):
        try:
            self._conn.close()
        except _:
            pass


class QueryBuilder:
    """
    composes the difference query between source relation and target relation
    """

    def __init__(self,
                 table_config: TableConfig,
                 columns: List[str]):
        self.table_config = table_config
        self.columns = columns

    def build(self, src_a, tgt_a) -> str:
        return \
            """
            SELECT {cols} 
            FROM 
            ({src_table}) {src_a} 
            FULL OUTER JOIN 
            ({tgt_table}) {tgt_a} 
            ON {join_cond} 
            WHERE NOT ({where_condition})
            """.format(cols=self._projection(src_a, tgt_a), src_table=self.table_config.src_relation, src_a=src_a,
                       tgt_table=self.table_config.tgt_relation, tgt_a=tgt_a,
                       join_cond=self._join_condition(src_a, tgt_a),
                       where_condition=self._where_condition(src_a, tgt_a))

    def _join_condition(self, src_a, tgt_a) -> str:
        data = ['{src_a}.{col} = {tgt_a}.{col}'.format(src_a=src_a, tgt_a=tgt_a, col=x)
                for x in self.table_config.join_cols]
        return ' AND '.join(data)

    def _where_condition(self, src_a, tgt_a) -> str:
        cols = [y for y in self.columns if y not in self.table_config.join_cols]
        data = ["{src_a}.{col} = {tgt_a}.{col}".format(src_a=src_a, tgt_a=tgt_a, col=x) for x in cols]
        return ' AND '.join(data)

    def _projection(self, src_a, tgt_a) -> str:
        data = ['{als}.{col}'.format(als=y, col=x) for x in self.columns for y in [src_a, tgt_a]]
        return ','.join(data)

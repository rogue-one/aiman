from typing import List

import psycopg2

from .config import DBConfig, TableConfig


class CursorWrapper:
    """
    a generator that wraps around the cursor and closes it once all data has been exhausted by the consumer.
    """

    def __init__(self, cursor, max_rows: int):
        self._cursor = cursor
        self.max_rows: int = max_rows

    def __iter__(self):
        x: int = 0
        for row in self._cursor:
            if x >= self.max_rows:
                break
            else:
                x += 1
                yield row
        try:
            self._cursor.close()
        except _:
            pass


class RelationFields:

    def __init__(self, keys: List[str], columns: List[str]):
        self.keys: List[str] = keys
        self.columns: List[str] = [x for x in columns if x not in keys]
        self._validate(columns)

    @staticmethod
    def _validate(columns):
        for x in columns:
            assert x in columns, 'key column %s not found in the relation' % x


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

    def sql_field_names(self, sql: str, keys: List[str]) -> RelationFields:
        query: str = "SELECT * FROM (%s) t0 WHERE 1 = 0" % sql
        cursor = self._conn.cursor()
        cursor.execute(query)
        return RelationFields(keys, [x.name for x in cursor.description])

    def query(self, sql: str, max_rows: int) -> CursorWrapper:
        cursor = self._conn.cursor()
        cursor.execute(sql)
        return CursorWrapper(cursor, max_rows)

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
                 fields: RelationFields):
        self.table_config = table_config
        self.fields = fields

    def build(self, src_a, tgt_a) -> str:
        return \
            """
            SELECT {cols} 
            FROM 
            ({src_table}) {src_a} 
            FULL OUTER JOIN 
            ({tgt_table}) {tgt_a} 
            ON {join_cond} 
            WHERE ({where_condition})
            """.format(cols=self._projection(src_a, tgt_a), src_table=self.table_config.src_relation, src_a=src_a,
                       tgt_table=self.table_config.tgt_relation, tgt_a=tgt_a,
                       join_cond=self._join_condition(src_a, tgt_a),
                       where_condition=self._where_condition(src_a, tgt_a))

    def _join_condition(self, src_a, tgt_a) -> str:
        data = ['{src_a}.{col} = {tgt_a}.{col}'.format(src_a=src_a, tgt_a=tgt_a, col=x)
                for x in self.fields.keys]
        return ' AND '.join(data)

    def _where_condition(self, src_a, tgt_a) -> str:
        cond1 = ["{src_a}.{col} = {tgt_a}.{col}".format(src_a=src_a, tgt_a=tgt_a, col=x) for x in self.fields.columns]
        cond2 = [' {als}.{col} IS NULL '.format(als=y, col=x) for x in self.fields.keys for y in [src_a, tgt_a]]
        return 'NOT ({cond1}) OR {cond2}'.format(cond1=' AND '.join(cond1), cond2=' OR '.join(cond2))

    def _projection(self, src_a, tgt_a) -> str:
        key = ['CASE WHEN {s}.{x} IS NULL THEN {t}.{x} ELSE {s}.{x} END as {x}'.format(s=src_a, t=tgt_a, x=x) for
                    x in self.fields.keys]
        rest = ['{als}.{col}'.format(als=y, col=x) for x in self.fields.columns for y in [src_a, tgt_a]]
        return ','.join(key + rest)

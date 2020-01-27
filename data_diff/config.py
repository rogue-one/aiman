#!/usr/bin/env python
from typing import List

import yaml


class TableConfig:
    """
    Config object expressing a single comparison config
    """

    SRC_RELATION = 'src-relation'
    TGT_RELATION = 'tgt-relation'
    KEYS = 'keys'

    def __init__(self, name: str, config: dict):
        self.name = name
        self.src_relation: str = config[TableConfig.SRC_RELATION]
        self.tgt_relation: str = config[TableConfig.TGT_RELATION]
        self.keys: List[str] = config[TableConfig.KEYS]


class DBConfig:
    HOSTNAME = 'hostname'
    USERNAME = 'username'
    PASSWORD = 'password'
    DEFAULT_DB = 'default_db'
    PORT = 'port'

    def __init__(self, config: dict):
        self.hostname: str = config[self.HOSTNAME]
        self.username: str = config[self.USERNAME]
        self.password: str = config[self.PASSWORD]
        self.default_db: str = config[self.DEFAULT_DB]
        self.port: int = config[self.PORT]


class AppConfig:
    MAX_ROWS = 'max-rows'
    DB_CONFIG = 'db-config'

    def __init__(self, config):
        self.max_rows: int = config.get(self.MAX_ROWS, 100)
        self.db_config: DBConfig = DBConfig(config[self.DB_CONFIG])


class ConfigParser:
    """
    This class parses the input config file and provides methods to lookup config entries
    """

    TABLE_CONFIG = 'table-config'
    APP_CONFIG = 'app-config'

    def __init__(self, conf_file: str):
        self._config: dict = self._parse_file(conf_file)
        self.app_config: AppConfig = AppConfig(self._config[ConfigParser.APP_CONFIG])

    @staticmethod
    def _parse_file(input_file: str) -> dict:
        """
        parses a yaml file
        :param input_file:
        :return: config python object
        """
        with open(input_file, 'r') as stream:
            return yaml.safe_load(stream)

    def relation(self, src_table: str) -> TableConfig:
        """
        fetch table config
        :param src_table:
        :return:
        """
        return TableConfig(src_table, self._config[ConfigParser.TABLE_CONFIG][src_table])

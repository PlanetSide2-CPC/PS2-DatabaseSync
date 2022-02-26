"""此模块实现了包的核心功能。"""
from abc import ABCMeta, abstractmethod

import pymongo
import pymysql

from hydrogen.shortcuts import read_config


class Database(metaclass=ABCMeta):
    """数据库的抽象接口。"""

    def __init__(self):
        self.config = read_config('database')

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def connect(self):
        """连接到数据库。

        Returns: None

        """

    @abstractmethod
    async def update(self, table_name, field):
        """动态创建和更新数据库。

        Args:
            table_name (str): 数据表名称。
            field (dict): 字段数据。

        Returns: None

        """

    @abstractmethod
    def close(self):
        """关闭连接。

        Returns: None

        """


class Mysql(Database):
    """Mysql 的具体接口。"""

    def __init__(self):
        super().__init__()
        self.cursor = None
        self.database_connect = None
        self.seperator = ', '

    def connect(self):
        self.database_connect = pymysql.connect(host=self.config.get('host'),
                                                user=self.config.get('user'),
                                                password=self.config.get('password'),
                                                database=self.config.get('database'),
                                                port=self.config.get('port'))
        self.cursor = self.database_connect.cursor()

    async def update(self, table_name, field):
        sql_key = self.seperator.join(key for key in field.keys())
        sql_value = self.seperator.join('"' + value + '"' for value in field.values())

        sql_insert = f'INSERT INTO {table_name} ({sql_key}) VALUES ({sql_value})'

        try:
            self.cursor.execute(sql_insert)
        except pymysql.Error:
            sql_create_key = self.seperator.join(key + ' varchar(255)' for key in field.keys())
            sql_create_table = f'CREATE TABLE {table_name} ' \
                               f'(id INT AUTO_INCREMENT, {sql_create_key}, PRIMARY KEY (id))'
            self.cursor.execute(sql_create_table)
            self.cursor.execute(sql_insert)
        finally:
            self.database_connect.commit()

    def close(self):
        self.cursor.close()
        self.database_connect.close()


class Mongodb(Database):
    """MongoDB 的具体接口"""

    def __init__(self):
        super().__init__()
        self.database_connect = None
        self.connect_url = self.config.get('url')

    def connect(self):
        client_connect = pymongo.MongoClient(self.connect_url)
        self.database_connect = client_connect[self.config.get('database')]

    async def update(self, table_name, field):
        collection = self.database_connect[table_name]
        collection.insert_one(field)

    def close(self):
        self.database_connect.close()


DATABASE_FACTORY = {
    "mysql": Mysql(),
    "mongodb": Mongodb()
}

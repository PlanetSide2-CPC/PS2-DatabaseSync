"""此模块实现了包的核心功能。"""
from abc import ABCMeta, abstractmethod

import pymysql
import pymongo

from hydrogen.shortcuts import read_config


class Database(metaclass=ABCMeta):
    """数据库的抽象接口。"""

    def __repr__(self):
        """实例的数据库连接状态"""

    @abstractmethod
    def update(self, table_name, field):
        """动态创建和更新数据库。

        Args:
            table_name (str): 数据表名称。
            field (dict): 字段数据。

        Returns: None

        """


class DatabaseFactory(metaclass=ABCMeta):
    """数据库的抽象工厂。"""

    def __repr__(self):
        """实例创建"""

    def create_database(self):
        """创建数据库的工厂。

        Returns: 数据库实例。

        """


class Mysql(Database):
    """Mysql 的具体接口。"""

    def __init__(self, config):
        """初始化数据库连接。

        Args:
            config (dict): 数据库配置信息。
        """
        self.seperator = ', '
        self.connect = pymysql.connect(host=config.get('host'),
                                       user=config.get('user'),
                                       password=config.get('password'),
                                       database=config.get('database'),
                                       port=config.get('port'))
        self.cursor = self.connect.cursor()

    def __repr__(self):
        return f"数据库已连接: {self.connect}"

    def update(self, table_name, field):
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
            self.connect.commit()


class Mongodb(Database):
    """MongoDB 的具体接口"""

    def __init__(self, config):
        def is_user_and_password_exist(username, password):
            if username == '':
                return False
            if password == '':
                return False
            return True

        def is_database_requirement_exist(host, port, database):
            if host == '':
                return False
            if port == '':
                return False
            if database == '':
                return ''
            return True

        def create_connect_url():
            connect_url = 'mongodb://'
            if is_user_and_password_exist(config.get('user'), config.get('password')):
                connect_url += f'{config.get("user")}:{config.get("password")}@'
            if is_database_requirement_exist(config.get('host'),
                                             config.get('port'),
                                             config.get('database')):
                connect_url += f'{config.get("host")}:{config.get("port")}/{config.get("database")}'
            return connect_url

        self.connect_url = create_connect_url()

        self.connect = pymongo.MongoClient(self.connect_url)
        self.database_connect = self.connect[config.get('database')]

    def __repr__(self):
        return f"数据库已连接：{self.connect}"

    def update(self, table_name, field):
        collection = self.database_connect[table_name]
        collection.insert_one(field)


class MongodbFactory(DatabaseFactory):
    """Mongo 的 工厂实现"""

    def __init__(self):
        self.config = read_config(key='database')

    def __repr__(self):
        return '实例创建成功'

    def create_database(self):
        return Mongodb(self.config)


class MysqlFactory(DatabaseFactory):
    """Mysql 的工厂创建。"""

    def __init__(self):
        self.config = read_config(key='database')

    def __repr__(self):
        return '实例创建成功'

    def create_database(self):
        return Mysql(self.config)

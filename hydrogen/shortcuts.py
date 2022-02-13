"""此模块实现部分功能的快捷实现方式。"""
import json


def read_config(key=None, filename='hydrogen/config/config.json'):
    """读取用户配置文件。

    从默认的配置文件读取配置，使用 json 的 load 载入。

    Args:
        key (str): 希望读取的键，默认读取所有。
        filename (str): 自定义配置文件路径，默认 config.json。

    Returns:
        dict: 配置文件的字典形式。

    """
    with open(filename, encoding='utf-8') as file:
        if key is None:
            return json.load(file)
        return json.load(file).get(key)

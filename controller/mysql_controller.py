import json

import pymysql


class Mysql(object):
    """数据库相关操作

    """

    def __init__(self):
        with open("config/config.json") as config:
            database = json.load(config)["database"]

        self.conn = pymysql.connect(host=database["host"], port=database["port"], db=database["database"],
                                    user=database["user"], password=database["password"])

    async def update_event_in_background(self, payload):
        pass


class DeathEventHandler(Mysql):
    """死亡事件

    """

    async def update_event_in_background(self, payload):
        """击杀数据库更新

        :param payload: Websocket 订阅数据，字典类。
        """
        with self.conn.cursor() as cursor:
            sql = "INSERT INTO ps2_death (attacker_character_id, attacker_fire_mode_id, attacker_loadout_id, " \
                  "attacker_vehicle_id, attacker_weapon_id, character_id, character_loadout_id, is_headshot, " \
                  "world_id, zone_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (payload["attacker_character_id"], payload["attacker_fire_mode_id"],
                                 payload["attacker_loadout_id"], payload["attacker_vehicle_id"],
                                 payload["attacker_weapon_id"], payload["character_id"],
                                 payload["character_loadout_id"], payload["is_headshot"],
                                 payload["world_id"], payload["zone_id"]))
            self.conn.commit()


class AlertEventHandler(Mysql):
    """警报事件

    """

    async def update_event_in_background(self, payload):
        """警报数据库更新

        :param payload: Websocket 订阅数据，字典类。
        """
        with self.conn.cursor() as cursor:
            sql = "INSERT INTO ps2_jingbao (faction_vs, faction_tr, faction_nc, world_id, zone_id, " \
                  "metagame_event_id, metagame_event_state) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (payload["faction_vs"], payload["faction_tr"], payload["faction_nc"],
                                 payload["world_id"], payload["zone_id"], payload["metagame_event_id"],
                                 payload["metagame_event_state"]))
            self.conn.commit()

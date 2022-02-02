"""This module contains all database operation."""
import logging

import mysql.connector

from ps2cpcdata import __config__

logger = logging.getLogger(__name__)


class Mysql(object):
    """Mysql database operation."""

    def __init__(self):
        self.database = __config__["database"]
        self.conn = mysql.connector.connect(**self.database)

    async def _update(self, insert_event, event):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(insert_event, event)
        except mysql.connector.errors.Error as err:
            logger.exception(err)
        else:
            self.conn.commit()
        finally:
            cursor.close()

    async def death(self, payload):
        """Update death event.

        Args:
            payload: Death event.

        Returns: None.

        """
        insert_death = "INSERT INTO ps2_death (attacker_character_id, attacker_fire_mode_id, attacker_loadout_id, " \
                       "attacker_vehicle_id, attacker_weapon_id, character_id, character_loadout_id, is_headshot, " \
                       "world_id, zone_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        death = (payload["attacker_character_id"], payload["attacker_fire_mode_id"], payload["attacker_loadout_id"],
                 payload["attacker_vehicle_id"], payload["attacker_weapon_id"], payload["character_id"],
                 payload["character_loadout_id"], payload["is_headshot"], payload["world_id"], payload["zone_id"])
        await self._update(insert_death, death)

    async def alert(self, payload):
        """Update death event.

        Args:
            payload: Alert event.

        Returns: None.

        """
        insert_alert = "INSERT INTO ps2_jingbao (faction_vs, faction_tr, faction_nc, world_id, zone_id, " \
                       "metagame_event_id, metagame_event_state) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        alert = ((payload["faction_vs"], payload["faction_tr"], payload["faction_nc"], payload["world_id"],
                  payload["zone_id"], payload["metagame_event_id"], payload["metagame_event_state"]))
        await self._update(insert_alert, alert)


if __name__ == '__main__':
    pass

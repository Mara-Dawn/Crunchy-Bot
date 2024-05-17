from typing import Any

from combat.enemies.types import EnemyType


class Encounter:

    def __init__(
        self,
        guild_id: int,
        enemy_type: EnemyType,
        max_health: int,
        message_id: int = None,
        id: int = None,
    ):
        self.guild_id = guild_id
        self.enemy_type = enemy_type
        self.max_health = max_health
        self.current_health = max_health
        self.message_id = message_id
        self.id = id

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "Encounter":
        from datalayer.database import Database

        if row is None:
            return None

        return Encounter(
            guild_id=int(row[Database.ENCOUNTER_GUILD_ID_COL]),
            enemy_type=EnemyType(row[Database.ENCOUNTER_ENEMY_TYPE_COL]),
            max_health=int(row[Database.ENCOUNTER_ENEMY_HEALTH_COL]),
            message_id=int(row[Database.ENCOUNTER_MESSAGE_ID_COL]),
            id=int(row[Database.ENCOUNTER_ID_COL]),
        )

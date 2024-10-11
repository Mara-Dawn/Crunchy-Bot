import datetime
from dataclasses import dataclass

import aiosqlite

from datalayer.database import Database


@dataclass
class Patch:
    command: str
    timestamp: datetime.datetime
    id: str


class DBPatcher:

    def __init__(self, database: Database):
        self.database = database
        self.patches: list[Patch] = []

        self.patches.append(
            Patch(
                command=f"""
                ALTER TABLE {self.database.ENCOUNTER_TABLE}
                ADD {self.database.ENCOUNTER_OWNER_ID_COL} INTEGER;
            """,
                timestamp=datetime.datetime(day=29, month=8, year=2024),
                id="encounter_owner",
            )
        )

        self.patches.append(
            Patch(
                command=f"""
                ALTER TABLE {self.database.COMBAT_EVENT_TABLE}
                ADD {self.database.COMBAT_EVENT_DISPLAY_VALUE} INTEGER;
            """,
                timestamp=datetime.datetime(day=30, month=8, year=2024),
                id="display_value_combat_events",
            )
        )

        self.patches.append(
            Patch(
                command=f"""
                ALTER TABLE {self.database.USER_GEAR_TABLE}
                ADD {self.database.USER_GEAR_SPECIAL_VALUE_COL} TEXT;
            """,
                timestamp=datetime.datetime(day=10, month=10, year=2024),
                id="gear_special_value",
            )
        )

    def get_patch(self, patch_id: str) -> Patch | None:
        for patch in self.patches:
            if patch.id == patch_id:
                return patch
        return None

    async def apply_patch(self, patch_id: str):
        patch = self.get_patch(patch_id)

        if patch is not None:
            async with aiosqlite.connect(self.database.db_file, timeout=20) as db:
                cursor = await db.execute(patch.command)
                insert_id = cursor.lastrowid
                await db.commit()
                return insert_id

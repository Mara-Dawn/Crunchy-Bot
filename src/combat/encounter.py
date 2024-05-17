import discord
from combat.enemies.enemy import Enemy
from items.item import Item


class Encounter:

    def __init__(
        self, enemy: Enemy, max_health: int, loot: dict[Item, int], id: int = None
    ):
        self.enemy = enemy
        self.max_health = max_health
        self.current_health = max_health
        self.loot = loot
        self.id = id

    def get_embed(self, show_info: bool = False) -> discord.Embed:
        title = "A random Enemy appeared!"

        embed = discord.Embed(title=title, color=discord.Color.blurple)

        enemy_name = f"> ~* {self.enemy.name} *~"
        content = "```python\n" '"{self.description}"' "```"
        embed.add_field(name=enemy_name, value=content, inline=False)

        if show_info:
            enemy_info = f"```ansi\n[37m{self.information}```"
            embed.add_field(name="", value=enemy_info, inline=False)
            return embed

        health = f"**health:** {self.current_health}/{self.max_health}\n"
        embed.add_field(name="", value=health, inline=False)

        embed.set_image(f"attachment://{self.enemy.image}")

        return embed

from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from combat.gear.droppable import Droppable
from combat.gear.types import Rarity
from combat.skills.skill import CharacterSkill, Skill
from control.controller import Controller
from control.types import SkillRefreshOption, UserSettingType
from events.bot_event import BotEvent


class PostEncounterState(State):

    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.POST_ENCOUNTER
        self.next_state: StateType = None

    async def startup(self):
        for combatant in self.context.combatants:
            member = combatant.member

            refresh_setting = await self.user_settings_manager.get(
                member.id, member.guild.id, UserSettingType.REFRESH_SKILLS
            )

            if refresh_setting == SkillRefreshOption.DISABLED:
                continue

            log_message = f"{member.display_name} auto refresh check started. {refresh_setting.value}"
            self.logger.log(member.guild.id, log_message, cog=self.log_name)

            spent_skills: dict[int, CharacterSkill] = {}
            spent_skill_types = set()

            for slot, skill in combatant.skill_slots.items():
                if skill is None:
                    continue
                if skill.rarity == Rarity.UNIQUE:
                    continue
                skill_data = await self.skill_manager.get_skill_data(combatant, skill)
                if (
                    skill_data.stacks_left() is not None
                    and skill_data.stacks_left() <= 0
                ):
                    spent_skills[slot] = skill_data
                    spent_skill_types.add(skill.type)

            log_message = f"{member.display_name} auto refresh: {len(spent_skills)} spent skills found."
            self.logger.log(member.guild.id, log_message, cog=self.log_name)

            if len(spent_skills) <= 0:
                continue

            user_skills = await self.database.get_user_skill_inventory(
                member.guild.id, member.id
            )

            log_message = f"{member.display_name} auto refresh skill types: "
            for skilltype in spent_skill_types:
                log_message += f"{skilltype.value}, "
            self.logger.log(member.guild.id, log_message, cog=self.log_name)

            filtered_skills: list[Skill] = []
            for skill in user_skills:
                if skill.type not in spent_skill_types:
                    continue
                if skill.rarity == Rarity.UNIQUE:
                    continue
                filtered_skills.append(skill)

            log_message = f"{member.display_name} auto refresh: {len(filtered_skills)} possible replacement skills found."
            self.logger.log(member.guild.id, log_message, cog=self.log_name)

            character_equipped_skills = combatant.skill_slots
            changes_made = False
            for slot, skill_data in spent_skills.items():

                log_message = f"{member.display_name} auto refresh: Finding replacement for {skill_data.skill.name} in slot {slot}."
                self.logger.log(member.guild.id, log_message, cog=self.log_name)

                replacement_skill = None
                for skill in filtered_skills:
                    if skill.type != skill_data.skill.type:
                        continue
                    match refresh_setting:
                        case SkillRefreshOption.SAME_RARITY:
                            if skill_data.skill.rarity == skill.rarity:
                                replacement_skill = skill
                                break
                        case SkillRefreshOption.HIGHEST_RARITY:
                            if (
                                replacement_skill is None
                                or Droppable.RARITY_SORT_MAP[skill.rarity]
                                > Droppable.RARITY_SORT_MAP[replacement_skill.rarity]
                            ):
                                replacement_skill = skill
                            if replacement_skill.rarity == Rarity.LEGENDARY:
                                break
                        case SkillRefreshOption.LOWEST_RARITY:
                            if (
                                replacement_skill is None
                                or Droppable.RARITY_SORT_MAP[skill.rarity]
                                < Droppable.RARITY_SORT_MAP[replacement_skill.rarity]
                            ):
                                replacement_skill = skill
                            if replacement_skill.rarity == Rarity.COMMON:
                                break

                if replacement_skill is None:
                    log_message = (
                        f"{member.display_name} auto refresh: found no replacements."
                    )
                    self.logger.log(member.guild.id, log_message, cog=self.log_name)
                    continue

                log_message = f"{member.display_name} auto refresh: found: {replacement_skill.name} with rarity {replacement_skill.rarity.value}."
                self.logger.log(member.guild.id, log_message, cog=self.log_name)

                character_equipped_skills[slot] = replacement_skill
                changes_made = True
                filtered_skills.remove(replacement_skill)

            if not changes_made:
                continue
            log_message = f"{member.display_name} auto refresh: applying changes."
            self.logger.log(member.guild.id, log_message, cog=self.log_name)

            await self.database.set_selected_user_skills(
                member.guild.id, member.id, character_equipped_skills
            )

        if self.context.opponent.defeated:
            self.next_state = StateType.LOOT_PAYOUT
            self.done = True
        else:
            self.context._concluded = True
            self.done = True
            self.quit = True

    async def handle(self, event: BotEvent) -> bool:
        return False

    async def update(self):
        pass

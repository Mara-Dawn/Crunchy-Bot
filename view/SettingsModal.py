import builtins
from typing import *
import discord

from BotSettings import BotSettings
from CrunchyBot import CrunchyBot

class SettingsModal(discord.ui.Modal):

    def __init__(self, bot: CrunchyBot, settings: BotSettings, cog: str, command: str, title: str, callback: Callable = None, callback_arguments: List[Any] = None):
        super().__init__(title=title)
        
        self.settings = settings
        self.bot = bot
        self.command = command
        self.cog = cog
        self.callback = callback
        self.callback_arguments = callback_arguments
        self.id_map: Dict[str, discord.ui.TextInput] = {}
        self.type_map: Dict[str, Type[Any]] = {}
        self.input_settings_map: Dict[str, Tuple[str,str]] = {}
        self.constraints: List[SettingsConstraint]  = []
        self.allow_negative_map: Dict[str, bool] = {}
    
    def add_field(self, guild_id: int, subsetting_key: str, setting_key: str, type: Type[Any], allow_negative: bool = False):
        label = self.settings.get_setting_title(subsetting_key, setting_key)
        default = self.settings.get_setting(guild_id, subsetting_key, setting_key)
        
        field_id = setting_key
        new_field = discord.ui.TextInput(label=label, required=False, custom_id=field_id)
        new_field.default = str(default)
        self.type_map[field_id] = type
        self.input_settings_map[field_id] = (subsetting_key, setting_key)
        self.allow_negative_map[field_id] = allow_negative
        self.id_map[field_id] = new_field
        self.add_item(new_field)
        
    def add_constraint(self, parameters: List[Any], callback: Callable[[Any], bool], on_error_message: str):
        new_constraint = SettingsConstraint(parameters, callback, on_error_message)
        self.constraints.append(new_constraint)
    
    def __cast_value(self, value: str, type: Type[Any]) -> Any:
        match type:
            case builtins.int:
                if not value.lstrip('-').isdigit():
                    return None
                try:
                    value = int(value)
                except ValueError:
                    return None
            case builtins.float:
                try:
                    value = float(value)
                except ValueError:
                    return None
        
        return value
    
    async def on_submit(self, interaction: discord.Interaction):
        
        errors: List[discord.ui.TextInput] = []
        
        for text_input_id, type in self.type_map.items():
            text_input = self.id_map[text_input_id]
            value = self.__cast_value(text_input.value, type)
            error = value is None
                
            if not error and not self.allow_negative_map[text_input_id]:
                error = value < 0
            
            if error:
                errors.append(text_input)
                
        if len(errors) != 0:
            message = f'Illegal values:\n{', \n'.join([f'{text_input.label} ({text_input.value})' for text_input in errors])}'
            await self.bot.response(self.cog, interaction, message, self.command, args=[text_input.value for text_input in self.children])
            return
        
        for constraint in self.constraints:
            values = []
            for argument in constraint.parameters:
                values.append(self.__cast_value(self.id_map[argument].value, self.type_map[argument]))
                
            if not constraint.callback(*values) :
                await self.bot.response(self.cog, interaction, 'Error:\n' + constraint.on_error_message, self.command, args=[text_input.value for text_input in self.children])
                return
            
        for text_input_id, keys in self.input_settings_map.items():
            value = self.__cast_value(self.id_map[text_input_id].value, self.type_map[text_input_id])
            self.settings.update_setting(interaction.guild_id, keys[0], keys[1], value)
            
        await self.bot.response(self.cog, interaction, f'Settings were successfully updated.', self.command, args=[text_input.value for text_input in self.children])
        
        if self.callback is not None:
            self.callback(*self.callback_arguments)
        
        
class SettingsConstraint():
    
    def __init__(self, parameters: List[Any], callback: Callable[[Any], bool], on_error_message: str):
        self.parameters = parameters
        self.callback = callback
        self.on_error_message = on_error_message
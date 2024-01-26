import json
from string import Formatter
from datetime import timedelta
from discord.ext import commands
import requests


class BotUtil():
    
    def strfdelta(tdelta, inputtype='timedelta'):

        if inputtype == 'timedelta':
            remainder = int(tdelta.total_seconds())
        elif inputtype in ['s', 'seconds']:
            remainder = int(tdelta)
        elif inputtype in ['m', 'minutes']:
            remainder = int(tdelta)*60
        elif inputtype in ['h', 'hours']:
            remainder = int(tdelta)*3600
        elif inputtype in ['d', 'days']:
            remainder = int(tdelta)*86400
        elif inputtype in ['w', 'weeks']:
            remainder = int(tdelta)*604800
            
        if remainder <= 0:
            return "0 minutes"

        possible_fields = ('weeks', 'days', 'hours', 'minutes', 'seconds')
        constants = {'weeks': 604800, 'days': 86400, 'hours': 3600, 'minutes': 60, 'seconds': 1}
        output = []
        for field in possible_fields:
            result, remainder = divmod(remainder, constants[field])
            
            if result > 0:
                output.append(str(result) + " " + field)
        
        if len(output) <= 1:
            return  ''.join(output)
        
        result = ', '.join([str(x) for x in output[:-1]])
        result += ' and ' + str(output[-1])
            
        return result.strip()

    def get_name(bot: commands.Bot, guild_id: int, user_id: int, max_len: int = 15):
            if bot.get_guild(guild_id) is None or bot.get_guild(guild_id).get_member(user_id) is None:
                return "User not found"
            name = bot.get_guild(guild_id).get_member(user_id).display_name
            name = (name[:max_len] + '..') if len(name) > max_len else name
            return name

class TenorImage(object):
    def __init__(self, data=None):
        if data:
            self.created = data.get('created')
            self.url = data.get('url')
            self.tags = data.get('tags')
            self.type = data.get('tupe')
            self.dims = ""
            self.preview = ""
            self.size = ""
            self.duration = ""


class Tenor(object):
    def __init__(self, token):
        self.api_key = token

    def _get(self, **params):
        params['key'] = self.api_key
        params['client_key'] = 'MaraBot'
        params['media_filter'] = 'gif'

        response = requests.get('https://tenor.googleapis.com/v2/search', params=params)

        results = json.loads(response.text)

        return results

    def search(self, tag, random=False, limit=None):
        params = {'q': tag}
        params['random'] = random
        if limit:
            params['limit'] = limit
        results = self._get(**params)
        return results

    async def random(self, tag):
        search_results = self.search(tag=tag, random=True, limit=50)
        gif = search_results['results'][0]['media_formats']['gif']['url']
        return gif

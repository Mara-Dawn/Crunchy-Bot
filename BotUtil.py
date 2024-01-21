from string import Formatter
from datetime import timedelta


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
        output = ""
        for field in possible_fields:
            result, remainder = divmod(remainder, constants[field])
            
            if result > 0:
                output += str(result) + " " + field + " "
               
        return output.strip()
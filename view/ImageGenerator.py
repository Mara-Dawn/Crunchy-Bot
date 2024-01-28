import io
import os
import random
import re

from MaraBot import MaraBot
from datalayer.Quote import Quote
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class ImageGenerator():

    def __init__(self, bot: MaraBot):
        self.bot = bot
        
        self.images_path = "./img/quote/"
        self.fonts_path = "./fonts/"
        
        self.images = [os.path.join(self.images_path, f) for f in os.listdir(self.images_path) if os.path.isfile(os.path.join(self.images_path, f))]
        self.image = None
        
        self.fonts = [os.path.join(self.fonts_path, f) for f in os.listdir(self.fonts_path) if os.path.isfile(os.path.join(self.fonts_path, f))]
        self.font_path = None
        self.font_size = None
        self.font = None
        self.anchor = None
        self.position = None
        self.align = None
    
    def randomize(self):
        image_path = self.images[random.randrange(len(self.images))]
        self.image = Image.open(image_path)
        
        self.font_path = self.fonts[random.randrange(len(self.fonts))]
        self.font_size = self.image.height//8
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        
        positions = [
            {
                'anchor': 'ma',
                'pos': (self.image.width//2,self.image.height//2),
                'align': 'center'
            },
            {
                'anchor': 'la',
                'pos': (self.image.width//10,self.image.height//10),
                'align': 'left'
            }
            # {
            #     'anchor': 'ra',
            #     'pos': (self.image.width - (self.image.width//10),self.image.height//10),
            #     'align': 'right'
            # }
        ]
        
        position_dict = random.choice(positions)
        self.anchor = position_dict['anchor']
        self.position = position_dict['pos']
        self.align = position_dict['align']
    
    def from_quote(self, quote: Quote) -> io.BytesIO:
        self.randomize()
        text = self.parse_text(quote)
        guild_id = quote.get_guild_id()
        
        max_text_width = self.image.width - (self.image.width//10) * 2
        max_text_height = int(self.image.height * 1/2)
        
        draw = ImageDraw.Draw(self.image)
        
        while True:
            text = self.wrap_text(text, self.font, max_text_width)
            self.font_size -= 1
            self.font = ImageFont.truetype(self.font_path, self.font_size)
            left, top, right, bottom = draw.textbbox(self.position, text, font=self.font, anchor=self.anchor)
            
            text_height = abs(top - bottom)
            
            if text_height < max_text_height or self.font_size <= 1:
                break
        
        stroke_width = self.font_size//15
        
        if self.anchor == 'ma':
            self.position = (self.position[0], self.image.height//2 - text_height//2)
        
        draw.multiline_text(self.position, f'{text}', (0, 0, 0), font=self.font, stroke_width=stroke_width, anchor=self.anchor, align=self.align, stroke_fill='white')
        
        author_position = (self.image.width - 15, self.image.height - 15)
        author_name = self.bot.get_guild(guild_id).get_member(quote.get_member()).display_name 
        if author_name is None:
            author_name = quote.get_member_name()
        
        author_text = f'- {author_name}'
        
        while self.font.getlength(author_text) > (max_text_width//2):
            self.font_size -= 1
            self.font = ImageFont.truetype(self.font_path, self.font_size)
        
        stroke_width = self.font_size//20
        draw.multiline_text(author_position, author_text, (0, 0, 0), font=self.font, anchor ="rd", stroke_width=stroke_width, stroke_fill='white')
        
        arr = io.BytesIO()
        self.image.save(arr, format='PNG')
        arr.seek(0)
        return arr
    
    def parse_text(self, quote: Quote) -> str:
        text = quote.get_message_content()
        
        mention_pattern = re.compile(r"<@!?(\d+)>")
        mentions = mention_pattern.findall(text)

        for mention in mentions:
            user = self.bot.get_guild(quote.get_guild_id()).get_member(int(mention))
            if user:
                text = text.replace(f"<@{mention}>", f"{user.display_name}")
                text = text.replace(f"<@!{mention}>", f"{user.display_name}")
        
        emoji_pattern = re.compile(r'<a?:([^:]+):\d+>')
        return emoji_pattern.sub(lambda m: f":{m.group(1)}:", text)
    
    def wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_text_width) -> str:
        lines = ['']
        for word in text.split():
            line = f'{lines[-1]} {word}'.strip()
            if font.getlength(line) <= max_text_width:
                lines[-1] = line
            else:
                lines.append(word)
        return '\n'.join(lines)
from imgurpython import ImgurClient
from PIL import ImageFont
from .configgen import get_config

def update_config():
    config = get_config()
    if config:
        client = ImgurClient(config['client_id'], config['client_secret'])
        return client

def upload_to_imgur(file):
    """Uploads a file to imgur.com"""
    image = update_config().upload_from_path(file, anon=True)
    return image['link']

def get_wrapped_text(text: str, font: ImageFont.ImageFont, line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)

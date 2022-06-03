from configparser import ConfigParser
import os

config_object = ConfigParser()

def write_config(id, secret):
    config_object['imgur'] = {
        'client_id': id,
        'client_secret': secret
    }
    with open(os.path.join(os.path.dirname(__file__), 'config.ini'), 'w') as configfile:
        config_object.write(configfile)

def check_for_config():
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'config.ini')):
        config_object.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        if not config_object.has_section('imgur'):
            return False
        if not config_object.has_option('imgur', 'client_id') or not config_object.has_option('imgur', 'client_secret'):
            return False
        elif config_object.has_option('imgur', 'client_id') and config_object.has_option('imgur', 'client_secret'):
            return True
    else:
        return False

def get_config():
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'config.ini')):
        if check_for_config():
            config_object.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
            return {
                'client_id': config_object['imgur']['client_id'],
                'client_secret': config_object['imgur']['client_secret']
            }
        else:
            return None
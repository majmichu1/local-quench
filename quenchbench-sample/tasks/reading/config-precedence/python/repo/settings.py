import os

from files import read_ini

DEFAULTS = {'port': 8000, 'debug': False}


def load_settings():
    merged = dict(DEFAULTS)
    merged.update(read_ini('config.ini'))
    if os.environ.get('APP_PORT'):
        merged['port'] = int(os.environ['APP_PORT'])
    return merged

from settings import load_settings


def start():
    s = load_settings()
    return f'listening on {s["port"]}'

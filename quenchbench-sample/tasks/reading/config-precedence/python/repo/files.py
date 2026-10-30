import configparser


def read_ini(path):
    cp = configparser.ConfigParser()
    cp.read(path)
    if not cp.has_section('server'):
        return {}
    return {'port': cp.getint('server', 'port', fallback=8000)}

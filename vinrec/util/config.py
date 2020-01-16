import configparser

class Config(object):

    instance = None
    @staticmethod
    def get(path=None):
        if Config.instance:
            return Config.instance
        if Config.instance is None and path is not None:
            return Config(path)
        return None

    def __init__(self, path):
        conf = configparser.ConfigParser()
        conf.read(path)
        Config.instance = conf

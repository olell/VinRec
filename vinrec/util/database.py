# Global imports
from peewee import SqliteDatabase

# Local imports
from vinrec.const.locations import DATABASE_PATH

class Database(object):

    instance = None

    @staticmethod
    def get():
        if Database.instance is None:
            return Database()()
        else:
            return Database.instance()
    
    def __init__(self):
        if Database.instance is not None:
            return
        Database.instance = self

        self.db = SqliteDatabase(DATABASE_PATH)

    def __call__(self):
        try:
            self.db.connect()
        except:
            pass
        return self.db
import sqlalchemy
from utils.config import Config


class ConnMysql:

    def __init__(self):
        self._cfg = Config()
        self._db_data = self._cfg.get_database()

    def connect_db(self, database='stock'):
        db_connect = sqlalchemy.create_engine(
            "mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8".format(
                self._db_data['user'],
                self._db_data['passwd'],
                'localhost',
                database
            )
        )
        return db_connect
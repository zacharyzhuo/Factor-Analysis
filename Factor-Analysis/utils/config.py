import socket
from configparser import ConfigParser


class Config:
    
    def __init__(self):
        self._local_config = ConfigParser()
        self._local_config.read('../config.ini', encoding='utf8')
        self._path_to_share_config = self._local_config["path"]["path_to_config"]

        '''
        TODO
        判斷本地或共享資料是否存在
        '''

        # 讀取共享設定檔
        self._config = ConfigParser()
        self._config.read(self._path_to_share_config, encoding='utf8')

    # 取用「設定檔」內資料庫參數
    def get_database(self):
        data = {
            "host": str(self._config["database"]["host"]),
            "port": int(self._config["database"]["port"]),
            "user": str(self._config["database"]["user"]),
            "passwd": str(self._config["database"]["passwd"]),
            "db": str(self._config["database"]["db"]),
            "charset": str(self._config["database"]["charset"]),
        }
        return data

    # 取用「設定檔」一般 section 的 key 之 value
    def get_value(self, section, key):
        value = self._config[section][key]
        return value

    @staticmethod
    def get_ip_address():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

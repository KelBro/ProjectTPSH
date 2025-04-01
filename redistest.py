from redis import StrictRedis as Sredis
from config_reader import config
from io import BytesIO
from PIL import Image

class Redis():
    def __init__(self):
        self.r = Sredis(host=config.ai_host.get_secret_value(), port=6379, password=config.ai_passwd.get_secret_value())

    def redisrun(self):
        print("Redis is running")
        while True:
            if self.r.exists('aitasks'):
                photoi = self.r.rpop('aitasks').decode('utf-8')
                photob = self.r.get(photoi+'b')
                self.r.set(photoi, "ПОКА ЧТО НИЧЕГО")


rds = Redis()
rds.redisrun()
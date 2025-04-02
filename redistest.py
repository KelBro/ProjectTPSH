from redis import StrictRedis as Sredis
from config_reader import config
from detectClothing import Classification
# Classification()
class Redis():
    def __init__(self):
        self.r = Sredis(host=config.ai_host.get_secret_value(), port=6379, password=config.ai_passwd.get_secret_value())
        self.img_path = 'img.jpg'

    def redisrun(self):
        print("Redis is running")
        while True:
            if self.r.exists('aitasks'):
                photo_request = self.r.rpop('aitasks')
                len_id = photo_request[0]
                photo_id = photo_request[1:len_id+1].decode(encoding='utf-8')
                photo_bytes = photo_request[len_id+1:]
                with open(self.img_path, 'wb') as img:
                    img.write(photo_bytes)
                self.r.set(photo_id, str(Classification.GetMark(self.img_path)))


rds = Redis()
rds.redisrun()
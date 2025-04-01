import random

from redis import StrictRedis as Sredis
from config_reader import config
from io import BytesIO
from PIL import Image


r = Sredis(host=config.ai_host.get_secret_value(), port=6379, password=config.ai_passwd.get_secret_value())
print("Redis is running")


photo_b = BytesIO()
photo = Image.open('../src.jpg')
photo.save(photo_b, 'JPEG')
photob = photo_b.getvalue()
photo_id = f'test-test-{random.randint(0, 10000000000)}'
r.lpush('aitasks', photo_id)
r.set(photo_id + 'b', photob)


photoi = r.rpop('aitasks').decode('utf-8')
photob = r.get(photoi + 'b')
print(type(photob))
with open('../img.jpg', 'wb') as img:
    img.write(bytes(photob))
r.set(photoi, "ПОКА ЧТО НИЧЕГО")



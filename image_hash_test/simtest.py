from PIL import Image
import imagehash

hash_size = 64
origin = Image.open('first.png')
first = imagehash.whash(origin, hash_size=hash_size)
firstp = imagehash.phash(origin, hash_size=hash_size)
firstd = imagehash.dhash(origin, hash_size=hash_size)
play = Image.open('third.png')
# play = play.resize((int(play.width / 2), int(play.height / 2)), resample=Image.LANCZOS)
# play = play.rotate(13, expand=1)
play.show()
second = imagehash.whash(play, hash_size=hash_size)
secondp = imagehash.phash(play, hash_size=hash_size)
secondd = imagehash.dhash(play, hash_size=hash_size)

print((first - second))
print((first - second)/(hash_size**2))
print((firstp - secondp)/(hash_size**2))
print((firstd - secondd))
print((firstd - secondd)/(hash_size**2))

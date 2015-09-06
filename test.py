import urllib
# from urllib import urlencode
from urllib2 import urlopen
import os
import pyglet

filename = 'transcript.wav'
url = "http://leapoffaith.mybluemix.net/t2s?text=hello&accept=audio%2Fwav&download=true"

urllib.urlretrieve (url, filename)

# pygame.init()
# song = pygame.mixer.Sound(filename)
# clock = pygame.time.Clock()
# song.play()
# while True:
#     clock.tick(60)
# pygame.quit()

os.system('play ' + filename)

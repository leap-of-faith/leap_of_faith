import requests

image = 'anthony.jpg'
data = open('./public/img/' + image, 'rb').read()
res = requests.post(url='http://leap-of-faith.mybluemix.net/imageProcess',
                    data=data,
                    headers={'Content-Type': 'image/jpeg'})

print "Done."
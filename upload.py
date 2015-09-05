import requests
import os
from alchemyapi_python.alchemyapi import AlchemyAPI
import json

# Minimum percent match for top tag to be used (over Wolfram)
ALCHEMY_MIN_PERC = .6

# Tracks returned data on an image (from Wolfram or Alchemy)
class ImageData:
	def __init__(self, img_location, api, response):
		self.img_location = img_location
		self.response = response
		self.api = api
		self.tags = []
		self.object = None
		self.object_perc = None

	def __str__(self):
		s = '\nImage: ' + self.img_location + ' is a ' + self.object + ' at ' + str(float(self.object_perc) * 100) + '% via ' + self.api + '.\n\n'
		s += '## Response Object ##\n'
		s += json.dumps(self.response, indent=4)

		s += '\n## Tags ##\n'
		for tag in self.tags:
			s += tag['text'] + ' : ' + tag['score']
		s += '\n'
		return s



# Runs an image through image processing APIs 
# Returns an ImageData object
def processImage(img_location):
	# Now process this image with Alchemy
	image_data = alchemy_processImage(img_location)
	return image_data
	

# Processes an image using the Alchemy API
# Return an ImageData object
def alchemy_processImage(img_location):
	response = AlchemyAPI().imageTagging('image', img_location)
	if response['status'] == 'OK':
		image_data = ImageData(img_location, 'alchemy', response)

		for keyword in response['imageKeywords']:
			image_data.tags.append(keyword)

		if len(response['imageKeywords']) > 0:
			image_data.object = response['imageKeywords'][0]['text']
			image_data.object_perc = response['imageKeywords'][0]['score']

		return image_data
	else:
		print('Error in image tagging call: ', response['statusInfo'])
	return None

# Processes the image using the Wolfram API
# Return an ImageData object
def wolfram_processImage(img_location):
	res = requests.post(
		url='http://leap-of-faith.mybluemix.net/processImage',
		data=data,
		headers={'Content-Type': 'image/jpeg'}
	)
	return ImageData('', 'wolfram', None)
	

image_data = processImage('./public/img/anthony.jpg')
print image_data


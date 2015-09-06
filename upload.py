import requests
import os
from alchemyapi_python.alchemyapi import AlchemyAPI
import json
from urllib import urlencode
from urllib2 import urlopen
from random import random
import unicodedata
# import wolfram

# Make sure to set your Wolfram App ID in the environment
# WOLFRAM_APP_ID = os["WOLFRAM_APP_ID"]

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
		self.imageFaces = None

	def __str__(self):
		s = '\nImage: ' + self.img_location + ' is a ' + self.object + ' at ' + str(float(self.object_perc) * 100) + '% via ' + self.api + '.\n\n'
		s += '## Response Object ##\n'
		s += json.dumps(self.response, indent=4)
 
		s += '\n## Tags ##\n'
		for tag in self.tags:
			s += tag['text'] + ' : ' + tag['score']
		s += '\n'

		if self.imageFaces != None:
			s += "Gender: " + self.imageFaces["gender"].lower() + ", Age: " + self.imageFaces["age_min"] + " to " + self.imageFaces["age_max"] + "\n";

		return s

# Takes in a local location in the file system
# Outputs a remote url from the internet where the image is hosted
def getRemoteUrl(local_location):
	pass # Todo @Anthony

# Runs an image through image processing APIs 
# Returns an ImageData object
def processImage(local_location):
	image_data = None
	if(local_location):
		# Now process this image with Alchemy
		image_data = alchemy_processImage(local_location, type='image')
		# Check if we need to get Wolfram data
		# if(image_data == None or float(image_data.object_perc) < ALCHEMY_MIN_PERC):
		# 	print 'Fetching data from Wolfram (', image_data.object_perc if image_data != None else 'None', ')'
		# 	remote_url_location = getRemoteUrl(local_location);
		# 	wolfram_image_data = wolfram_processImage(remote_url_location)
		# 	if(wolfram_image_data != None):
		# 		if(image_data == None or float(image_data.object_perc) > float(wolfram_image_data.object_perc)): 
		# 			image_data = wolfram_image_data
		
		# Fetch face data if there is a person in the image
		if(image_data != None and image_data.object.lower() == "person"):
			image_data = analyze_face(image_data)

	return image_data

# Wraps the object name from the image in a random sentence.
# Returns a string
def tagToSentence(image_data):
	text = image_data.object;
	if(len(image_data.imageFaces) > 0):
		# It is a person and we have a face
		
		sentences = [];
		if(image_data.imageFaces["gender"].lower() == "male"):
			sentences = ['There\'s a man in front of you. He is between the ages of {0} and {1}.']
		else:
			sentences = ['There\'s a woman in front of you. She is between the ages of {0} and {1}.']

		index = int(round(random() * (len(sentences) - 1)))
		return sentences[index].format(str(image_data.imageFaces["age_min"]), str(image_data.imageFaces["age_max"]));
	else:
		sentences = ['A {0} is in your proximity.',
					 'Holy moly, is that a {0}?',
					 'I spy a {0}.',
					 'That looks like a positively wonderful {0}',
					 'That would be a {0}.',
					 'That looks like a tiger. Oh sorry, that is a {0}. My bad.'];
		if(image_data.object == None):
			sentences = ["What an incredible...thing.", "That's a thing, for sure.", "One thing. Right ahead.", "I'm not answering your questions, you locked me in this bag."]
		index = int(round(random() * (len(sentences) - 1)))
		return sentences[index].format(str(text));

# Processes an image using the Alchemy API
# Type can be image if the image is local
# Return an ImageData object
def alchemy_processImage(img_location, type = 'url'):
	try:
		response = AlchemyAPI().imageTagging(type, img_location)
		if response['status'] == 'OK':
			image_data = ImageData(img_location, 'alchemy', response)

			for keyword in response['imageKeywords']:
				image_data.tags.append(keyword)

			if len(response['imageKeywords']) > 0:
				image_data.object = response['imageKeywords'][0]['text']
				image_data.object_perc = response['imageKeywords'][0]['score']

			return image_data
	except:
		print('Error in image tagging call: ', response['statusInfo'])
	return None

# Processes an image with a person in it and attempts to return 
# information on the age and gender of the person
# Returns a dictionary of data
def analyze_face(image_data):
	response = AlchemyAPI().faceTagging('image', image_data.img_location)

	if response['status'] == 'OK':
		if(len(response['imageFaces']) > 0):
			print response['imageFaces'];
			age_range = response['imageFaces'][0]['age']['ageRange']
			age_range = unicodedata.normalize('NFKD', age_range).encode('ascii', 'ignore')
			age_min = 0
			age_max = 100
			if('-' in age_range):
				age_min = age_range[0:age_range.index('-')]
				age_max = age_range[age_range.index('-') + 1:]
			elif('<' in age_range):
				age_min = 0
				age_max = age_range[age_range.index('<') + 1:]
			image_data.imageFaces = {
				"gender": response['imageFaces'][0]['gender']['gender'],
				"age_min": age_min,
				"age_max": age_max
			}
	return image_data


class WolframCloud:

    def wolfram_cloud_call(self, **args):
        arguments = dict([(key, arg) for key, arg in args.iteritems()])
        result = urlopen("http://www.wolframcloud.com/objects/1da937e5-1080-4b72-b9b8-f9ffd193dc6a", urlencode(arguments))
        return result.read()

    def call(self, url):
        textresult = self.wolfram_cloud_call(url=url)
        return textresult

def parseResult(rawResult):
	truncate = rawResult.index("->")+3
	return (rawResult[21:rawResult.index("::")],rawResult[truncate:truncate+4])

# Processes the image using the Wolfram API
# Return an ImageData object
def wolfram_processImage(img_location):
	cloud = WolframCloud()
	image_data = None

	# Attempt to process the image via Wolfram's API
	try:
		wolfram_result = parseResult(cloud.call(img_location))
		# Convert it to an ImageData structure
		image_data = ImageData(img_location, 'wolfram', wolfram_result)
		# Save the results
		image_data.tags = [{
			"text": wolfram_result[0],
			"score": wolfram_result[1]
		}]
		image_data.object = wolfram_result[0]
		image_data.object_perc = wolfram_result[1]
	except:
		pass
	
	return image_data

# Python function for sending the text to Bluemix to be spoken
# Takes a location of the image as a URL
def imageToText(img_location):
	image_data = processImage(img_location)
	print image_data
	sentence = tagToSentence(image_data)
	print sentence
	return sentence


if __name__ == '__main__':
	imageToText('./public/img/sean.jpg')



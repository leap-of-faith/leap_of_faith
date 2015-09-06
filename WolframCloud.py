from urllib import urlencode
from urllib2 import urlopen

class WolframCloud:

    def wolfram_cloud_call(self, **args):
        arguments = dict([(key, arg) for key, arg in args.iteritems()])
        result = urlopen("http://www.wolframcloud.com/objects/1da937e5-1080-4b72-b9b8-f9ffd193dc6a", urlencode(arguments))


#http://www.wolframcloud.com/objects/d6286319-3ac5-4c34-91d8-e04a250f1843

        return result.read()

    def call(self, url):
        textresult =  self.wolfram_cloud_call(url=url)
        return textresult

def parseResult(rawResult):
	truncate = rawResult.index("->")+3

	return (rawResult[21:rawResult.index("::")],rawResult[truncate:truncate+4])

def process(imgURL):
	cloud = WolframCloud()
	result = None

	try:
		result = parseResult(cloud.call(imgURL))
	except:
		result = "Failed to identify the image."

	return result

def displayResult(result):
	return "You're facing a " + result[0] + " with " + result[1] + " probability."

def main():
	url = "http://kindersay.com/files/images/soccer-ball.png"

	result = process(url)
	print displayResult(result)

if __name__ == '__main__':
	main()
from urllib import urlencode
from urllib2 import urlopen

class WolframCloud:

    def wolfram_cloud_call(self, **args):
        arguments = dict([(key, arg) for key, arg in args.iteritems()])
        result = urlopen("http://www.wolframcloud.com/objects/d6286319-3ac5-4c34-91d8-e04a250f1843", urlencode(arguments))
        return result.read()

    def call(self, url):
        textresult =  self.wolfram_cloud_call(url=url)
        return textresult

def parseResult(rawResult):
	return rawResult[19:rawResult.index("::")]

def process(imgURL):
	cloud = WolframCloud()
	result = ""

	try:
		result = "A " + parseResult(cloud.call(imgURL)) + " is in your vicinity."
	except:
		result = "Failed to identify the image."

	return result

def main():
	url = "http://kindersay.com/files/images/soccer-ball.png"

	print process(url)



if __name__ == '__main__':
	main()
/**
 * GET /
 * Home page.
 */

var bluemix      = require('./../node_modules/watson-developer-cloud/lib/bluemix'),
 	watson       = require('watson-developer-cloud');

exports.index = function(req, res) {
	res.render('index');
}

/**
 * POST /t2s
 * OPTIONS
 * 		TEXT: text to be transcribed
 * 		VOICE: Defaults to "en-US_MichaelVoice"
 * 		DOWNLOAD: Boolean
 * 		ACCEPT: What format to recieve
 * 		
 * Converts text to speech 
 */

exports.t2s = function(req, res) {
	console.log("Text-to-speech request received.");
	// Access the text-to-speech service via Bluemix proxy
	//var credentials = bluemix.getServiceCreds('text-to-speech');
	var credentials = bluemix.serviceStartsWith('text_to_speech');
	credentials["version"] = 'v1';
	console.log(credentials);
	var textToSpeech = watson.text_to_speech(credentials);
	var transcript = textToSpeech.synthesize(req.query);
	
	transcript.on('response', function(response) {
		if (req.query.download) {
			response.headers['content-disposition'] = 'attachment; filename=transcript.wav';
		}
	});
	
	transcript.on('error', function(error) {
		console.log('Synthesize error: ', error)
	});

	transcript.pipe(res);
}


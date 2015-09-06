/*eslint-env node*/

'use strict'

/**
 * Module dependencies.
 */
var server = require('http').createServer(),
	express = require('express'),
	compress = require('compression'),
//	favicon = require('serve-favicon'),
	bodyParser = require('body-parser'),
	logger = require('morgan'),
	session = require('express-session'),
	errorHandler = require('errorhandler'),
	lusca = require('lusca'),
	path = require('path'),
	assets = require('connect-assets'),
	sass = require('node-sass'),
	cfenv = require('cfenv'),
	WebSocketServer = require('ws').Server,
	wss = new WebSocketServer({
		server: server,
		path: '/websocket'
	});

/**
 * Controllers (route handlers).
 */
var homeController = require('./controllers/home');

/**
 * API keys.
 */
var secrets = require('./config/secrets.conf');

/**
 * Create Express server.
 */
var app = express();

/**
 * Express configuration.
 */
app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
app.use(compress());
app.use(assets({
  paths: ['public/css', 'public/js']
}));
app.use(logger('dev'));
//app.use(favicon(path.join(__dirname, 'public/favicon.png')));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
// app.use(session({
//   resave: true,
//   saveUninitialized: true,
//   secret: secrets.sessionSecret
// }));
// app.use(lusca({
//   csrf: true,
//   xframe: 'SAMEORIGIN',
//   xssProtection: true
// }));
app.use(express.static(path.join(__dirname, 'public'), { maxAge: 31557600000 }));

/**
 * Web Sockets for tracking connected devices
 * Courtesy of @geek on Github
 * https://github.com/geek/pebble-socket-example
 */
var webSockets = [];
var last_photo_trigger = 0;
var PHOTO_DELAY = 200; //ms

wss.on('connection', function(ws) {
	console.log("user connected");
	ws.on('message', function(message) {
		console.log("Received Message: %s", message);

		if(message.substring(0, 5) == 'photo') {
			// Verify that enough time has passed to allow another photo
			if((Date.now() - last_photo_trigger > PHOTO_DELAY)) {
				var photo_data = message.substring(6);
				// The user triggered a photo event
				console.log("Photo event triggered");
				last_photo_trigger = Date.now();
				// Notify the Leap to take a photo
				ws.send('takePicture:' + photo_data)
			}
		} 
		else if(message.substring(0, 8) == 'vibrate:') {
			console.log('Vibration intensity event triggered');
			var intensity = message.substring(8);
			if(intensity != '') {
				intensity = parseInt(intensity)
				// Send the vibration
				console.log(intensity);
				if(intensity > 20) {
					// Trigger low intensity
					broadcast('low');
				}
				else if(intensity > 15) {
					// Trigger medium intensity
					broadcast('med');
				}
				else if(intensity >= 0) {
					// Trigger high intensity
					broadcast('high');
				}
				// else no vibration triggered
			}
		}
	});
	ws.on('error', function(err) {
		console.log("Websocket custom error: error occurred");
		console.log(err);
	});
	// Notify Pebble's of connection
	ws.send('Connected to Bluemix');
});

/**
 * Use to broadcast data to Pebble
 */
function broadcast(data) {
	wss.clients.forEach(function each(client) {
		try {
			client.send(data);
		} catch(e) {
			console.log("failed client send");
		}
	});
};

/**
 * Primary app routes.
 */
app.get('/', homeController.index);
app.get('/t2s', homeController.t2s);
// app.get('/vibrate', function(req, res) {
// 	var intensity = req.query.intensity;
// 	if(intensity != undefined) {
// 		// Send the vibration
// 		console.log(intensity);
// 		if(intensity > 15) {
// 			// Trigger low intensity
// 			broadcast('low');
// 		}
// 		else if(intensity > 5) {
// 			// Trigger medium intensity
// 			broadcast('med');
// 		}
// 		else if(intensity >= 0) {
// 			// Trigger high intensity
// 			broadcast('high');
// 		}
// 		// else no vibration triggered
// 	}
// 	res.render('index');
// });

/**
 * Error Handler.
 */
app.use(errorHandler());

// get the app environment from Cloud Foundry
var appEnv = cfenv.getAppEnv();

// start server on the specified port and binding host
server.on('request', app);
server.listen(appEnv.port, function() {
	// print a message when the server starts listening
	console.log("server starting on " + appEnv.url + ", port: " + appEnv.port, ", socket port: " + server.address().port);
});

module.exports = app;

/*eslint-env node*/

'use strict'

/**
 * Module dependencies.
 */
var express = require('express'),
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
	Hapi = require('hapi'),
	Ws = require('ws');

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
var server = new Hapi.Server();
var port = process.env.VCAP_APP_PORT || 8888;
server.connection({
	host: 'localhost',
	port: port
});

server.start(function () {
	console.log("server started on port " + port);
    var ws = new Ws.Server({ server: server.listener });
    console.log("websocket setup");
    ws.on('connection', function (socket) {
    	console.log("connection made");
        socket.send('Welcome');
    });

    webSockets.push(ws);
});

/**
 * Use to transmit data to Pebble
 */
var transmit = function (data) {
    try {
        webSockets.forEach(function (ws) {

            if (!ws || !ws.clients) {
                return;
            }

            for (var i = 0, il = ws.clients.length; i < il; ++i) {
                var client = ws.clients[i];
                if (client && client.send) {
                    client.send(data.toString());
                }
            }
        });
    }
    catch (err) {}
};

/**
 * Primary app routes.
 */
app.get('/', homeController.index);
app.get('/t2s', homeController.t2s);
app.post('/processImage', homeController.processImage);
app.get('/vibrate', function(req, res) {
	var intensity = req.query.intensity;
	if(intensity != undefined) {
		// Send the vibration
		console.log(intensity);
		transmit(intensity);
	}
	res.render('index');
});

/**
 * Error Handler.
 */
app.use(errorHandler());

// get the app environment from Cloud Foundry
var appEnv = cfenv.getAppEnv();

// start server on the specified port and binding host
app.listen(appEnv.port, function() {

	// print a message when the server starts listening
	console.log("server starting on " + appEnv.url);
});

module.exports = app;

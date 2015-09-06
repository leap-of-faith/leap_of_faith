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
// var server = new Hapi.Server();
// var port = process.env.VCAP_APP_PORT || 8888;
// server.connection({
// 	host: 'localhost',
// 	port: port
// });

wss.on("open", function(ev) {
	// ev?
	console.log("web socket opened");
});

wss.on('connection', function(ws) {
	console.log("user connected");
	ws.on('message', function(message) {
		console.log("Received %s", message);
	});

	ws.send('Hi Sean');
});

// server.start(function () {
// 	console.log("server started on port " + port);
//     var ws = new Ws.Server({ server: server.listener });
//     console.log("websocket setup");
//     ws.on('open', function() {
//     	console.log("websocket opened");
//     });
//     ws.on('connection', function (socket) {
//     	console.log("connection made");
//         socket.send('Welcome');
//     });
//     ws.on('message', function(socket) {
//     	console.log("message received");
//     	socket.send("Received Message");
//     });

//     webSockets.push(ws);
// });

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
server.on('request', app);
server.listen(appEnv.port, function() {
	// print a message when the server starts listening
	console.log("server starting on " + appEnv.url + ", port: " + appEnv.port, ", socket port: " + server.address().port);
});

module.exports = app;

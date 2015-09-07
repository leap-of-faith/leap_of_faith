// import
var UI = require('ui');
var Vibe = require('ui/vibe');

// buffer and socket
var buffer = "";
var ws = new window.WebSocket('wss://leap-of-faith.mybluemix.net/websocket');

// 500ms loop for proximity vibration feedback
window.setInterval(function() {
  if (buffer == "single" || buffer == "double" || buffer == "long") {
    Vibe.vibrate(buffer);
    buffer = "";
  }
}, 1000);

// socket connection successfully established
ws.onopen = function(event) {
  var card = new UI.Card();
  card.title('HELL YEAH!');
  card.show();
};

// socket error
ws.onerror = function(event) {
  var card = new UI.Card();
  card.title('oh noez');
  card.show();
};

// read data
ws.onmessage = function(event) { 
  var data = event.data;
  console.log(data);

  if (data == "low") {
    buffer = "single";
  } else if (data == "med") {
    buffer = "double";
  } else if (data == "high") {
    buffer = "long";
  }
};

// main window
var main = new UI.Card({
  title: 'PLEASE GIMME DATA'
});
main.show();

// take photo and identify the object
main.on('click', 'select', function(e) {
  ws.send("photo");
  Vibe.vibrate("short");
});

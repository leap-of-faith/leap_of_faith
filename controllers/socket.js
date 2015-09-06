/* Courtesy of @geek on Github
 * https://github.com/geek/pebble-socket-example */

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
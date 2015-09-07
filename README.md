
# FeelVision (aka "Leap" of Faith)
aka we can't think of good hackathon names

![alt text](https://raw.githubusercontent.com/leap-of-faith/leap_of_faith/master/public/img/sean_dancing.jpg "Such dance skills. Much 90s.")


# TLDR
Leap Motion + Python + IBM Bluemix + Wolfram Cloud + Node.JS + Pebble

# Demo

Bluemix image processing demo: https://youtu.be/epSx9_eQhzI

# How it works

The blind person (the user) wears two special gloves that each have an attached Leap Motion in the palm of the glove. This leap motion is hooked up to a computer hoisted in a bag on the user's back. The Leap Motion devices act as proximity sensors using their IR cameras.

The Leap Motions then continuously communicate with the base computer which runs the leap driver python script. The host computer calculates the proximity and sends this via an open websocket to a Node.js application running on a Bluemix server.

The Bluemix server takes the proximity and converts it down to 3 levels (low, med, high) that indicate what frequency to use for haptic feedback to the user. This frequency level is transmitted over 2 other websockets that are opened with the two Pebbles (one on each arm). The Pebbles will monitor these vibration requests and vibrate on a delay (every 500ms) to prevent the vibration requests from short-circuiting each other. This haptic feedback ques the user as to which direction obstacles or objects are in and how close they are to them.

At any time, the user can also press one of the buttons on Pebble to trigger either Leap Motion to take a photo. The request travels backwards through the websockets (Pebble > Bluemix > Host Computer > Leap Motion) and causes the Leap Motion to save an individual frame. This frame is then passed thorugh IBM Watson's AlchemyVision API and a custom-built image recognition API on Wolfram Cloud in order to determine the contents of the photo. Wolfram and Watson compete against each other and we choose the one that is most confident. If they determine that there is a person in the photo, then we further run the image through AlchemyVision Face Detection/Recognition in order to determine the gender and age, if possible, from the image. The data that we are able to collect from the image is then combined together into a cohesive sentence and sent back to the Bluemix server where it is fed into Watson's text-to-speech API. The voice is encoded into a .WAV file and downloaded onto the host computers where it is played aloud for the user to hear.

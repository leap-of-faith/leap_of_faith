from PIL import Image
import numpy as np
import ctypes
import scipy.misc
import requests
import math
from websocket import create_connection
from upload import imageToText

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

RANGE = 25.0  # 25cm max range of leap motion device
MAX_INTENSITY = 255.0  # max value of a pixel in a Leap Motion Frame Image
variable = ""

class SampleListener(Leap.Listener):
    pfobj = ''
    _count = 0
    _threshold = .90 * RANGE  # The point at which an object will be considered in range of the leap
    _ws = ""

    def on_init(self, controller):
        # Establish websocket connection to Bluemix
        self._ws = create_connection("ws://leap-of-faith.mybluemix.net/websocket")
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        self._ws.close()
        print "Exited"

    def calc_distance(self, image_array):
        """Returns the average distance of items in the image from the leap"""
        """
        #x_val = (1 - np.mean(image_array)/255) * 25
        x_val = (np.mean(image_array)/255) * 25
        #x_val = np.mean(image_array)
        print "x is ", x_val
              #((1)/(x+(1/255)))-(1/5)
        val = x_val  # ((1.0)/(x_val+(1.0/25.0)))-(1.0/255.0)
        #val = (1.0/(x_val+(1.0/MAX_INTENSITY)) - (1.0/RANGE))
        print "mean is ", np.mean(image_array), "max is ", MAX_INTENSITY, "range is ", RANGE, "val is ", val
        print "1/m ", 1.0/MAX_INTENSITY
        print "1/r", 1.0/RANGE
        print "1/(avg+(1/m)) ", (1.0/(np.mean(image_array)+(1.0/MAX_INTENSITY)))
        """
        return (1 - np.mean(image_array)/255) * 25

    def undistort(self, leap_image):  
        """Corrects for Leap Motion fisheye effect"""
        raw = leap_image.data
        distortion_buffer = leap_image.distortion
        distortion_width = leap_image.distortion_width
        width = leap_image.width
        height = leap_image.height

        corrected_width = 320
        corrected_height = 120
        corrected = np.empty((corrected_width, corrected_height), dtype=np.ubyte)

        for i in range(0, corrected_width):
            for j in range(0, corrected_height):
                # Calculate position in the calibration map
                calibrationX = 63.0 * i / corrected_width
                calibrationY = 62.0 * (1.0 - (j* 1.0)/corrected_height)

                # Fractional part to be used as weighting in bilinear interpolation
                weightX = calibrationX - math.trunc(calibrationX)
                weightY = calibrationY - math.trunc(calibrationY)

                # Get x,y coordinates of the closest calibration map points to the target pixel
                x1 = math.trunc(calibrationX)
                y1 = math.trunc(calibrationY)
                x2 = x1 + 1
                y2 = y1 + 1

                # Find x,y grid coordinates from distortion buffer
                dX1 = distortion_buffer[x1 * 2 + y1 * distortion_width]
                dX2 = distortion_buffer[x2 * 2 + y1 * distortion_width]
                dX3 = distortion_buffer[x1 * 2 + y2 * distortion_width]
                dX4 = distortion_buffer[x2 * 2 + y2 * distortion_width]
                dY1 = distortion_buffer[x1 * 2 + y1 * distortion_width + 1]
                dY2 = distortion_buffer[x2 * 2 + y1 * distortion_width + 1]
                dY3 = distortion_buffer[x1 * 2 + y2 * distortion_width + 1]
                dY4 = distortion_buffer[x2 * 2 + y2 * distortion_width + 1]

                # Bilinear Interpolation of target pixel
                dX = dX1*(1.0 - weightX)*(1.0 - weightY) + dX2*weightX*(1.0 - weightY) + dX3*(1.0 - weightX)*weightY + dX4*weightX*weightY
                dY = dY1*(1.0 - weightX)*(1.0 - weightY) + dY2*weightX*(1.0 - weightY) + dY3*(1.0 - weightX)*weightY + dY4*weightX*weightY

                #print "i,j ", i, j, " cal x,Y ", calibrationX, calibrationY, " weightX,Y ", weightX, weightY, " dX,Y ", dX, dY

                # Reject points outside [0..1]
                if dX>=0 and dX<=1 and dY>=0 and dY<=1:
                    # Denormalise points from [0..1] to [0..width] or [0..height]
                    denormalisedX = math.trunc(dX * width)
                    denormalisedY = math.trunc(dY * height)
                    corrected[i,j] = raw[denormalisedX + denormalisedY * width]
                else:
                    corrected[i,j] = 0

        corrected_image = Image.fromarray(corrected, 'L')
        return corrected_image
        
    def on_frame(self, controller):
        """Process a Leap Motion frame"""
        # Get the most recent frame and report some basic information
        frame = controller.frame() 

        # Get the two images that make up the frame (left camera, right camera)
        for index in range(len(frame.images)):
            image = frame.images[index]
            image_buffer_ptr = image.data_pointer
            ctype_array_def = ctypes.c_ubyte * image.width * image.height

            # as ctypes array
            as_ctype_array = ctype_array_def.from_address(int(image_buffer_ptr))
            # as numpy array
            image_array = np.ctypeslib.as_array(as_ctype_array)

            dist = self.calc_distance(image_array)  # distance of object from the leap motion

            # print some stats
            #print "avg: ", np.mean(image_array), ", max: ",  np.amax(image_array), ", min: ", np.amin(image_array), ", dist:", dist

            # buzz the watch as objects come into the range of the leap
            if dist < self._threshold:
                # buzz the watch
                self._ws.send('vibrate:%d' % int(dist))

            # buzz the watch as objects come into the range of the leap
            if dist < self._threshold:
                # buzz the watch
                self._ws.send('vibrate:%d' % int(dist))

            # if watch_button_pressed: then submit image to bluemix
            web_socket_data = self._ws.recv()
            if web_socket_data[0:12] == "takePicture:":
                print "watch button pressed!"
                location = 'public/img/fixed.jpg'
                self.undistort(image).save(location)
                textToSay = imageToText(location)
                filename = 'transcript.wav'
                url = "http://leapoffaith.mybluemix.net/t2s?" + urlencode({"text": textToSay, "accept": 'audio/wav', "download": true})

                urllib.urlretrieve (url, filename)
                # r = urlopen("http://leapoffaith.mybluemix.net/t2s?" + urlencode({"text": textToSay, "download": true})
                # r.read()
                os.system('play ' + filename)

        # Set Policy to collect images
        controller.set_policy(Leap.Controller.POLICY_IMAGES)

        status = "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
              frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))
        print status
        #self._ws.send(status)

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
        print "rdline"
    except KeyboardInterrupt:
        print "kbd interupt"
        pass
    finally:
        # Remove the sample listener when done
        print "finally"
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()

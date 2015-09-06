from PIL import Image
import numpy as np
import ctypes
import scipy.misc
import requests

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

RANGE = 25  # 25cm max range of leap motion device

class SampleListener(Leap.Listener):
    pfobj = ''
    _count = 0

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def calc_distance(self, image_array):
        """Returns the average distance of items in the image from the leap"""
        return (1 - np.mean(image_array)/255) * RANGE

        
    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame() 

        # Get Images
        print len(frame.images)
        print len(controller.images)
        for index in range(len(frame.images)):
            image = frame.images[index]
            print image
            print "height: ", image.distortion_height
            #imagedata = ctypes.cast(leap_image.data.cast().__long__(), ctypes.POINTER(leap_image.width * leap_image.height * ctypes.c_ubyte)).contents
            #image = np.frombuffer(imagedata, dtype = 'uint8')
            #image.shape = (image.height, image.width)
            image_buffer_ptr = image.data_pointer
            ctype_array_def = ctypes.c_ubyte * image.width * image.height

            # as ctypes array
            as_ctype_array = ctype_array_def.from_address(int(image_buffer_ptr))
            # as numpy array
            image_array = np.ctypeslib.as_array(as_ctype_array)

            print "avg: ", np.mean(image_array), ", max: ",  np.amax(image_array), ", min: ", np.amin(image_array), ", dist:", self.calc_distance(image_array)
            # if distance < threshold: then buzz watch
            # if watch_button_pressed: then submit image to bluemix
            """
            scipy.misc.toimage(image_array, cmin=0.0, cmax=1.0).save('outfile.jpg')
            exit(0)
                image = 'outfile.jpg'
                data = open('./public/img/' + image, 'rb').read()
                res = requests.post(url='http://leap-of-faith.mybluemix.net/processImage',
                                    data=data,
                                    headers={'Content-Type': 'image/jpeg'})
            """
        # Get Images
        controller.set_policy(Leap.Controller.POLICY_IMAGES)
        #print "bg frame policy: ", Leap.Controller.POLICY_BACKGROUND_FRAMES
        #print "images policy: ", Leap.Controller.POLICY_IMAGES
        #print "optimize hmd policy: ", Leap.Controller.POLICY_OPTIMIZE_HMD

        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
              frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))


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
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
####### Modification of Tensorflow Object Detection for SmartDoor #######
#
# This program uses a TensorFlow Lite model to perform object detection on a live webcam feed.
# It keeps a list of people of interest in order to determine if a person has entered a house
# or not. This is program would be ran two raspberry pies: one inside, and one outside.
#
# This code is based off of the Tensor Flow Lite Object Detection on Android and Rasbperry Pi at:
# https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md
#  
# We added modifications to record when a person appears and communicate with our fog device.

#Debugging
ONLINE = True

# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import time
import calendar
import socket
from threading import Thread
import importlib.util
from collections import defaultdict

# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(640,480),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()
	# Variable to control when the camera is stopped
        self.stopped = False
    def start(self):
	# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self
    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return
            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
    def read(self):
	# Return the most recent frame
        return self.frame
    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True
if __name__ == '__main__':
    # Define and parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                        required=True)
    parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                        default='detect.tflite')
    parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                        default='labelmap.txt')
    parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                        default=0.5)
    parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support the resolution entered, errors may occur.',
                        default='1280x720')
    parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                        action='store_true')

    # Add argument for either outside or inside camera
    parser.add_argument('--location', help='Where the camera is physically located',
                       choices=['inside','outside'], required=True)
    parser.add_argument('--host', help='server ip', required=True)
    parser.add_argument('--port', help='server port', required=True)
	
    args = parser.parse_args()

    #Set location of camera, ip and port
    in_or_out = args.location # set location of camera
    host = args.host  # as both code is running on same pc
    port = int(args.port)  # socket server port number

    
    MODEL_NAME = args.modeldir
    GRAPH_NAME = args.graph
    LABELMAP_NAME = args.labels
    min_conf_threshold = float(args.threshold)
    resW, resH = args.resolution.split('x')
    imW, imH = int(resW), int(resH)
    use_TPU = args.edgetpu
    # Import TensorFlow libraries
    # If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
    # If using Coral Edge TPU, import the load_delegate library
    pkg = importlib.util.find_spec('tflite_runtime')
    if pkg:
        from tflite_runtime.interpreter import Interpreter
        if use_TPU:
            from tflite_runtime.interpreter import load_delegate
    else:
        from tensorflow.lite.python.interpreter import Interpreter
        if use_TPU:
            from tensorflow.lite.python.interpreter import load_delegate
    # If using Edge TPU, assign filename for Edge TPU model
    if use_TPU:
        # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
        if (GRAPH_NAME == 'detect.tflite'):
            GRAPH_NAME = 'edgetpu.tflite'       
    # Get path to current working directory
    CWD_PATH = os.getcwd()
    # Path to .tflite file, which contains the model that is used for object detection
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)
    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)
    # Load the label map
    with open(PATH_TO_LABELS, 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    # Have to do a weird fix for label map if using the COCO "starter model" from
    # https://www.tensorflow.org/lite/models/object_detection/overview
    # First label is '???', which has to be removed.
    if labels[0] == '???':
        del(labels[0])
    # Load the Tensorflow Lite model.
    # If using Edge TPU, use special load_delegate argument
    if use_TPU:
        interpreter = Interpreter(model_path=PATH_TO_CKPT,
                                  experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
        print(PATH_TO_CKPT)
    else:
        interpreter = Interpreter(model_path=PATH_TO_CKPT)
    interpreter.allocate_tensors()
    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    floating_model = (input_details[0]['dtype'] == np.float32)
    input_mean = 127.5
    input_std = 127.5
    # Initialize frame rate calculation
    frame_rate_calc = 1
    freq = cv2.getTickFrequency()
    # Initialize video stream
    videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
    time.sleep(1)

    ### Additional code for Smartdoor ###
    people_list = defaultdict(lambda: False) #list of desired objects to detect i.e. specific people
                                             #keeps track if object detected during buffer cycle
    people_list['person'] = False
    people_list['banana'] = False
    people_list['fork'] = False
    people_list['scissors'] = False
    
    #Objects not detected every frame, so we have to keep a buffer to prevent oscillation
    frame_counter = 0
    frame_count = 5 #use a 5 frame buffer instead of checking every frame
    buffer_check = defaultdict(lambda:False,people_list) #Make a dict to track object present that frame
    
    if ONLINE:
        client_socket = socket.socket()  # instantiate
        client_socket.connect((host, port))  # connect to the server
    
    #for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    try:
        while True:

            # Start timer (for calculating frame rate)
            t1 = cv2.getTickCount()
            # Grab frame from video stream
            frame1 = videostream.read()
            # Acquire frame and resize to expected shape [1xHxWx3]
            frame = frame1.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)
            # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std
            # Perform the actual detection by running the model with the image as input
            interpreter.set_tensor(input_details[0]['index'],input_data)
            interpreter.invoke()
            # Retrieve detection results
            boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
            classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
            scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
            #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

            # Loop over all detections and draw detection box if confidence is above minimum threshold
            for i in range(len(scores)):
                if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                    # Get bounding box coordinates and draw box
                    # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
#                     ymin = int(max(1,(boxes[i][0] * imH)))
#                     xmin = int(max(1,(boxes[i][1] * imW)))
#                     ymax = int(min(imH,(boxes[i][2] * imH)))
#                     xmax = int(min(imW,(boxes[i][3] * imW)))

#                     cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
                    
                    # Draw label
                    object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index

                    ### MY CODE ###
                    curr_time = (calendar.timegm(time.gmtime()) - 1590390000)%86400 #get minutes since midnight pst

                    if object_name in people_list:
                        buffer_check[object_name] = True
                        if not people_list[object_name]:
                            people_list[object_name] = True
                            print(f"camera {object_name} {in_or_out} {curr_time}")
                            if ONLINE:
                                message = f"camera {object_name} {in_or_out} {curr_time}"
                                client_socket.send(message.encode())
#                                 data = client_socket.recv(1024).decode()  # receive response
#                                 print('Received from server: ' + data)  # show in terminal
                                
#                     label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
#                     labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
#                     label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
#                     cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
#                     cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

            frame_counter += 1
            if frame_counter>=frame_count:
                for object_detected in people_list:
                    if (not buffer_check[object_detected]) and people_list[object_detected]:
                        people_list[object_detected] = False
#                         print(f"camera {object_detected} exit {curr_time}")
#                         if ONLINE:
#                             message = f"camera {object_detected} exit {curr_time}"
#                             client_socket.send(message.encode())
#                             data = client_socket.recv(1024).decode()  # receive response
#                             print('Received from server: ' + data)  # show in terminal
                    frame_counter = 0
                    buffer_check[object_detected] = False

# #             Draw framerate in corner of frame
#             cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
            
            # All the results have been drawn on the frame, so it's time to display it.
            cv2.imshow('Object detector', frame)

 #         # Calculate framerate
#             t2 = cv2.getTickCount()
#             time1 = (t2-t1)/freq
#             frame_rate_calc= 1/time1
            
            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break

        # Clean up
        if ONLINE:
            client_socket.close()  # close the connection
        cv2.destroyAllWindows()
        videostream.stop()
    except socket.error:
        if ONLINE:
            client_socket.close()
        cv2.destroyAllWindows()
        videostream.stop()

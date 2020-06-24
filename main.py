print("hello")
import numpy as np
import cv2

class Config:
    gauss_blur = 25
    t1 = 127
    scale_factor = .4
    new_size = [0,0]
    pixel_count = 0
    lightness = 120
    saturation = 100
    yellow_green = 30
    blue_green = 100

BLUE = 0
GREEN = 1
RED = 2

def handle_gauss_blur(arg1):
    Config.gauss_blur = arg1
    if Config.gauss_blur % 2 == 0:
        Config.gauss_blur = Config.gauss_blur + 1

def handle_lightness(arg1):
    Config.lightness = arg1

def handle_saturation(arg1):
    Config.saturation = arg1

def handle_yellow_green(arg1):
    Config.yellow_green = arg1

def handle_blue_green(arg1):
    Config.blue_green = arg1

prev_frame = []

# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar("gauss_blur", "window1", 0, 255, handle_gauss_blur)
cv2.createTrackbar("lightness", "window1", 0, 255, handle_lightness)
cv2.createTrackbar("saturation", "window1", 0, 255, handle_saturation)
cv2.createTrackbar("yellow_green", "window1", 0, 255, handle_yellow_green)
cv2.createTrackbar("blue_green", "window1", 0, 255, handle_blue_green)

cv2.setTrackbarPos("gauss_blur", "window1", Config.gauss_blur)
cv2.setTrackbarPos("lightness", "window1", Config.lightness)
cv2.setTrackbarPos("saturation", "window1", Config.saturation)
cv2.setTrackbarPos("yellow_green", "window1", Config.yellow_green)
cv2.setTrackbarPos("blue_green", "window1", Config.blue_green)


video_capture = cv2.VideoCapture(0)

# get first frame
ret, frame = video_capture.read()

# for scaling
width = len(frame[0])
height = len(frame)
print (width, height)

Config.new_size = (int(width * Config.scale_factor), int(height * Config.scale_factor))
Config.pixel_count = Config.new_size[0] * Config.new_size[1]

nth = 0

while(True):

    # nth += 1

    # resize
    frame = cv2.resize(frame, Config.new_size)
    blurred_frame = cv2.GaussianBlur(frame, (Config.gauss_blur, Config.gauss_blur), cv2.BORDER_CONSTANT)


     # Convert BGR to HSV
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    # hue (0 to 180), saturation, brightness
    # red to yellow, but not into gree
    in_range1 = cv2.inRange(hsv, 
        (0, Config.saturation, Config.lightness), 
        (Config.yellow_green, 255, 255))
    in_range2 = cv2.inRange(hsv, 
        (Config.blue_green, Config.saturation, Config.lightness), 
        (180, 255, 255))
    in_range_all = cv2.bitwise_or(in_range1, in_range2)

    in_range1 = cv2.cvtColor(in_range1, cv2.COLOR_GRAY2BGR)
    in_range2 = cv2.cvtColor(in_range2, cv2.COLOR_GRAY2BGR)
    in_range_all = cv2.cvtColor(in_range_all, cv2.COLOR_GRAY2BGR)
        
    row1 = np.hstack([in_range1, in_range2])
    row2 = np.hstack([frame, in_range_all])
    images = np.vstack([row1, row2])

    cv2.imshow('window1',images)

    # detect window closing
    key = cv2.waitKey(1) 

    if key == 27: # escape key
        break

    if cv2.getWindowProperty("window1",cv2.WND_PROP_AUTOSIZE)  < 1: # closed with X       
        break   

    # get next frame
    prev_frame = frame
    ret, frame = video_capture.read()

# clean up
video_capture.release()
cv2.destroyAllWindows()

print("goodbye")


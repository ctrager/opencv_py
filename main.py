import numpy as np
import cv2
import time

# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

class Config:
    saturation = 90
    lightness = 20
    yellow_green = 40
    blue_green = 100
    
def handle_saturation(val):
    Config.saturation = val
cv2.createTrackbar("saturation", "window1", 0, 255, handle_saturation)
cv2.setTrackbarPos("saturation", "window1", Config.saturation)

def handle_lightness(val):
    Config.lightness = val
cv2.createTrackbar("lightness", "window1", 0, 255, handle_lightness)
cv2.setTrackbarPos("lightness", "window1", Config.lightness)

def handle_yellow_green(val):
    Config.yellow_green = val
cv2.createTrackbar("yellow_green", "window1", 0, 180, handle_yellow_green)
cv2.setTrackbarPos("yellow_green", "window1", Config.yellow_green)

def handle_blue_green(val):
    Config.blue_green = val
cv2.createTrackbar("blue_green", "window1", 0, 180, handle_blue_green)
cv2.setTrackbarPos("blue_green", "window1", Config.blue_green)


def prep_frame_for_video(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    in_range1 = cv2.inRange(hsv, 
        (0, Config.saturation, Config.lightness), 
        (Config.yellow_green, 255, 255))
    
    in_range2 = cv2.inRange(hsv, 
        (Config.blue_green, Config.saturation, Config.lightness), 
        (180, 255, 255))

    in_range_all_gray = cv2.bitwise_or(in_range1, in_range2)

    gray_without_red = cv2.bitwise_and(gray, gray, mask=255-in_range_all_gray)
    gray_without_red_bgr = cv2.cvtColor(gray_without_red, cv2.COLOR_GRAY2BGR)

    just_red = cv2.bitwise_and(frame, frame, mask=in_range_all_gray)
    
    both = cv2.bitwise_or(gray_without_red_bgr, just_red)

    img = np.hstack([frame, both])

    return img


video_capture = cv2.VideoCapture(0)
#video_capture = cv2.VideoCapture(
#    "rtsp://admin:password1@10.0.0.7:554/cam/realmonitor?channel=1&subtype=0")

# 
# get first frame
ret, frame = video_capture.read()

while(True):

    frame = prep_frame_for_video(frame)

    cv2.imshow("window1", frame)

    # detect window closing
    key = cv2.waitKey(1) 

    if key == 27: # escape key
        break

    if cv2.getWindowProperty("window1",cv2.WND_PROP_AUTOSIZE)  < 1: # closed with X       
        break   

    # get next frame
    ret, frame = video_capture.read()

# clean up
video_capture.release()
cv2.destroyAllWindows()

print("goodbye")

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

    frame = cv2.resize(frame, (320,240))

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

    return [frame, both]


video_capture = cv2.VideoCapture(0)
#video_capture = cv2.VideoCapture(
#    "rtsp://admin:password1@10.0.0.7:554/cam/realmonitor?channel=1&subtype=0")

# 
# get first frame
ret, frame = video_capture.read()
prev_frame = prep_frame_for_video(frame)[1]

def current_milliseconds():
    return round(time.time() * 1000)

prev_time = current_milliseconds()

while(True):

    now = current_milliseconds()

    frames = prep_frame_for_video(frame)

    if now - prev_time > 500:
        # print(now)
        
        curr_frame = frames[1]

        #cv2.imshow("diff", np.hstack((curr_frame, prev_frame)))
  
        curr_sum = np.sum(curr_frame, dtype=np.int64)
        prev_sum = np.sum(prev_frame, dtype=np.int64)

        diff = abs(curr_sum - prev_sum)
        pct = round((diff/prev_sum) * 100)

        print(diff, curr_sum, prev_sum, pct)
        prev_time = now
        
        prev_frame = curr_frame

    cv2.imshow("window1", np.hstack(frames))

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

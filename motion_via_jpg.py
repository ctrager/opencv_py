print("hello")
import numpy as np
import cv2
import time

class Config:
    gauss_blur = 25

def current_milliseconds():
    return round(time.time() * 1000)

def process_frame(frame):
    small = cv2.resize(frame, (320,240))
    return small

prev_frame = []

# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

video_capture = cv2.VideoCapture(0)

# get first frame
ret, frame = video_capture.read()

prev_frame = process_frame(frame)



prev_time = current_milliseconds()


while(True):

    curr_frame = process_frame(frame)
    now = current_milliseconds()
    if now - prev_time > 1500:
 
        diff = cv2.absdiff(curr_frame, prev_frame)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        nonzero = cv2.countNonZero(diff_gray)

        print("nonzero=", nonzero)        

        result, curr_jpg = cv2.imencode('.jpg', curr_frame)
        result, prev_jpg = cv2.imencode('.jpg', prev_frame)

        motion_score = abs(len(curr_jpg) - len(prev_jpg)) 

        print(nonzero, motion_score)    
        prev_frame = curr_frame
        prev_time = now    

    cv2.imshow("window1", np.hstack((curr_frame, prev_frame)))

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


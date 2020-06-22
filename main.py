print("hello")
import numpy as np
import cv2

class Config:
    g1 = 21
    g2 = 21
    t1 = 127
    t2 = 255
    scale_factor = .5

def myfunc(arg):
    print(arg)

def handle_gauss1(arg1):
    Config.g1 = arg1
    if Config.g1 % 2 == 0:
        Config.g1 = Config.g1 + 1

def handle_gauss2(arg1):
    Config.g2 = arg1
    if Config.g2 % 2 == 0:
        Config.g2 = Config.g2 + 1

def handle_thresh1(arg1):
    Config.t1 = arg1

def handle_thresh2(arg1):
    Config.t2 = arg1


#myfunc("corey")


video_capture = cv2.VideoCapture(0)

cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar("gauss1", "window1", 0, 255, handle_gauss1)
cv2.createTrackbar("gauss2", "window1", 0, 255, handle_gauss2)
cv2.createTrackbar('thresh1', 'window1', 0, 255, handle_thresh1)
cv2.createTrackbar('thresh2', 'window1', 0, 255, handle_thresh2)

cv2.setTrackbarPos("gauss1", "window1", Config.g1)
cv2.setTrackbarPos("gauss2", "window1", Config.g2)
cv2.setTrackbarPos("thresh1", "window1", Config.t1)
cv2.setTrackbarPos("thresh2", "window1", Config.t2)

ret, frame = video_capture.read()

# for scaling
width = len(frame[0])
height = len(frame)
print (width, height)

new_size = (int(width * Config.scale_factor), int(height * Config.scale_factor))

prev_frame = []

while(True):
 
    # resize
    frame = cv2.resize(frame, new_size)

    # gray scale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # blur it
    blurred_frame = cv2.GaussianBlur(gray_frame, (Config.g1, Config.g2), cv2.BORDER_CONSTANT)

    # convert it to color so that we can work with matching arrays
    bgr_gray_blurred_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_GRAY2BGR)

    if len(prev_frame) == 0:
        images = np.hstack([frame, bgr_gray_blurred_frame])
    else:
        diff = cv2.absdiff(blurred_frame, prev_frame)
        thresh = cv2.threshold(diff, Config.t1, Config.t2, cv2.THRESH_BINARY)[1]
        row1 = np.hstack([frame, bgr_gray_blurred_frame])
        diff = cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        row2 = np.hstack([diff, thresh])
        images = np.vstack([row1, row2])

    # arrange arrays side by side
 
    # display it
    cv2.imshow("window1",images)
 
    # detect window closing
    key = cv2.waitKey(1) 

    if key == 27: # escape key
        break

    if cv2.getWindowProperty("window1",cv2.WND_PROP_AUTOSIZE)  < 1: # closed with X       
        break   

    # get next frame
    prev_frame = blurred_frame
    ret, frame = video_capture.read()

# clean up
video_capture.release()
cv2.destroyAllWindows()

print("goodbye")


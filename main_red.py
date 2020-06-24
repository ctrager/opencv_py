print("hello")
import numpy as np
import cv2

class Config:
    g1 = 21
    g2 = 21
    t1 = 20
    scale_factor = .5
    new_size = [0,0]
    pixel_count = 0


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

# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar("gauss1", "window1", 0, 255, handle_gauss1)
cv2.createTrackbar("gauss2", "window1", 0, 255, handle_gauss2)
cv2.createTrackbar('thresh1', 'window1', 0, 255, handle_thresh1)

cv2.setTrackbarPos("gauss1", "window1", Config.g1)
cv2.setTrackbarPos("gauss2", "window1", Config.g2)
cv2.setTrackbarPos("thresh1", "window1", Config.t1)

prev_frame = []

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

    
    # blur it
    blurred_frame = cv2.GaussianBlur(frame, (Config.g1, Config.g2), cv2.BORDER_CONSTANT)
   
    if len(prev_frame) == 0:
        images = np.hstack([frame, frame])
    else:
        frame2 = np.copy(blurred_frame)
        for rows in frame2:
            for pixel in rows:
                pixel[0] = 0
                pixel[1] = 0
        frame3 = cv2.threshold(frame2, 127, 255, cv2.THRESH_BINARY)[1]
        images = np.hstack([frame, blurred_frame, frame2, frame3])

    # display it
    cv2.imshow("window1",images)
 
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


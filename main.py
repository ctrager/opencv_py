print("hello")
import numpy as np
import cv2

class Config:
    g1 = 21
    g2 = 21
    g3 = 0

def myfunc(arg):
    print(arg)

def handler1(arg1):
    #print("handler", arg1)
    Config.g1 = arg1
    if Config.g1 % 2 == 0:
        Config.g1 = Config.g1 + 1

def handler2(arg1):
    #print("handler", arg1)
    Config.g2 = arg1
    if Config.g2 % 2 == 0:
        Config.g2 = Config.g2 + 1

def handler3(arg1):
    print("handler", arg1)

#myfunc("corey")


video_capture = cv2.VideoCapture(0)

cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar("parm1", "window1", 0, 255, handler1)
cv2.createTrackbar("parm2", "window1", 0, 255, handler2)
#cv2.createTrackbar('parm3', 'w1', 0, 255, handler3)

cv2.setTrackbarPos("parm1", "window1", Config.g1)
cv2.setTrackbarPos("parm2", "window1", Config.g2)

ret, frame = video_capture.read()

# for scaling
width = len(frame[0])
height = len(frame)
print (width, height)
scale_factor = .5
new_size = (int(width * scale_factor), int(height * scale_factor))

while(True):
 
    # resize
    frame = cv2.resize(frame, new_size)

    # gray scale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # blur it
    blurred_frame = cv2.GaussianBlur(gray_frame, (Config.g1, Config.g2), cv2.BORDER_CONSTANT)

    # convert it to color so that we can work with matching arrays
    colored_blurred_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_GRAY2BGR)

    # arrange arrays side by side
    row1 = np.hstack([frame, colored_blurred_frame])

    # display it
    cv2.imshow('window1',row1)
 
    # improve this to detect closing of window better
    key = cv2.waitKey(1) 
    print(key)
    if key == 27:  #& 0xFF == ord('q'):
        break

    # get next frame
    ret, frame = video_capture.read()

# clean up
video_capture.release()
cv2.destroyAllWindows()

print("goodbye")


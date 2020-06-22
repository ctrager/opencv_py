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
    print("handler", arg1)
    Config.g1 = arg1
    if Config.g1 % 2 == 0:
        Config.g1 = Config.g1 + 1

def handler2(arg1):
    print("handler", arg1)
    Config.g2 = arg1
    if Config.g2 % 2 == 0:
        Config.g2 = Config.g2 + 1

def handler3(arg1):
    print("handler", arg1)

myfunc("corey")


cap = cv2.VideoCapture(0)

cv2.namedWindow("w1", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("w2", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("w3", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar('parm1', 'w1', 0, 255, handler1)
cv2.createTrackbar('parm2', 'w1', 0, 255, handler2)
cv2.createTrackbar('parm3', 'w1', 0, 255, handler3)

# char TrackbarName[50];
#   sprintf( TrackbarName, "Alpha x %d", alpha_slider_max );
#   createTrackbar( TrackbarName, "Linear Blend", &alpha_slider, alpha_slider_max, on_trackbar );
#Note the following (C++ code):

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # print(frame.width, frame.height)
    #break
    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame

    # for row in frame:
    #     for p in row:
    #         #break
    #         p[0] = 0
    #         #p[1] = 0
    #         p[2] = 0

    #frame_after = cv2.Canny(frame, 100, 100)

    #frame = imutils.resize(frame, width=500)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blured = cv2.GaussianBlur(gray, (Config.g1, Config.g2), cv2.BORDER_CONSTANT)

    cv2.imshow('w1',frame)
    cv2.imshow('w2',gray)
    cv2.imshow('w3',blured)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
#cv2.destroyAllWindows().destroyAllWindows()

print("goodbye")

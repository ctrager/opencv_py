print("hello")
import numpy as np
import cv2

def myfunc(arg):
    print(arg)

def handler(arg):
    print("handler", arg)

myfunc("corey")


cap = cv2.VideoCapture(0)

cv2.namedWindow("w1", cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('parm1','w1',0,255,handler)

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

    cv2.imshow('w1',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
#cv2.destroyAllWindows().destroyAllWindows()

print("goodbye")

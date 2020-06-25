import numpy as np
import cv2
import time

# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

class Config:
    gauss_blur = 25
    canny1 = 100
    canny2 = 100
    width = 1920
    height = 1080
    crop_y1 = 0
    crop_y2 = 900
    crop_x1 = 495
    crop_x2 = 1425
    # new size is 930 X 900
    new_size_for_analysis = (310,300) # 1/3 size
    new_size_for_video = (620,600) # 2/2 size    

def handle_canny1(val):
    Config.canny1 = val
def handle_canny2(val):
    Config.canny2 = val
def handle_gauss_blur(arg1):
    Config.gauss_blur = arg1
    if Config.gauss_blur % 2 == 0:
        Config.gauss_blur = Config.gauss_blur + 1    
cv2.createTrackbar("canny1", "window1", 0, 300, handle_canny1)
cv2.createTrackbar("canny2", "window1", 0, 300, handle_canny2)
cv2.setTrackbarPos("canny1", "window1", Config.canny1)
cv2.setTrackbarPos("canny2", "window1", Config.canny2)
cv2.createTrackbar("gauss_blur", "window1", 0, 255, handle_gauss_blur)
cv2.setTrackbarPos("gauss_blur", "window1", Config.gauss_blur)


def prep_frame_for_video(frame):
    img = frame[Config.crop_y1:Config.crop_y2, Config.crop_x1:Config.crop_x2]
    img = cv2.resize(img, Config.new_size_for_video)
    img = cv2.GaussianBlur(img, (Config.gauss_blur, Config.gauss_blur), cv2.BORDER_CONSTANT)

    return img


#video_capture = cv2.VideoCapture(0)
video_capture = cv2.VideoCapture(
    "rtsp://admin:password1@10.0.0.7:554/cam/realmonitor?channel=1&subtype=0")

# 
# get first frame
ret, frame = video_capture.read()

while(True):

    frame = prep_frame_for_video(frame)

    #frame2 = cv2.Canny(frame,Config.canny1,Config.canny2)

    
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

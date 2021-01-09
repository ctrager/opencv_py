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
    kernel_factor = 7  
    kernel = np.ones((kernel_factor,kernel_factor),np.uint8)
    dilate_iterations = 1

blob_params = cv2.SimpleBlobDetector_Params()

# Filter by Area.
blob_params.filterByArea = True
blob_params.minArea = 3000
blob_params.maxArea = 20000

# Filter by Circularity
blob_params.filterByCircularity = False
blob_params.minCircularity = 0.1

# Filter by Convexity
blob_params.filterByConvexity = False
blob_params.minConvexity = 0.87

# Filter by Inertia
blob_params.filterByInertia = False
blob_params.minInertiaRatio = 0.01

blob_params.minDistBetweenBlobs = 0.0
blob_params.filterByColor = False

blob_params.filterByColor = False
#params.blobColor = 255;


def handle_gauss_blur(arg1):
    Config.gauss_blur = arg1
    if Config.gauss_blur % 2 == 0:
        Config.gauss_blur = Config.gauss_blur + 1  
#cv2.createTrackbar("gauss_blur", "window1", 0, 255, handle_gauss_blur)
#cv2.setTrackbarPos("gauss_blur", "window1", Config.gauss_blur)

def handle_kernel(arg1):
    Config.kernel_factor = arg1
    Config.kernel = np.ones((Config.kernel_factor,Config.kernel_factor),np.uint8)
cv2.createTrackbar("kernel", "window1", 1, 20, handle_kernel)
cv2.setTrackbarPos("kernel", "window1", Config.kernel_factor)

def handle_dilate_iterations(arg1):
    Config.dilate_iterations = arg1
cv2.createTrackbar("dilate_iterations", "window1", 0, 20, handle_dilate_iterations)
cv2.setTrackbarPos("dilate_iterations", "window1", Config.dilate_iterations)

def handle_min_area(arg1):
    blob_params.minArea = arg1
cv2.createTrackbar("blob_params.minArea", "window1", 1, 5000, handle_min_area)
cv2.setTrackbarPos("blob_params.minArea", "window1", int(blob_params.minArea))


#video_capture = cv2.VideoCapture(0)
video_capture = cv2.VideoCapture(
    "rtsp://admin:password1@10.0.0.7:554/cam/realmonitor?channel=1&subtype=0")

# 
# get first frame
ret, frame = video_capture.read()
width = len(frame[0])
height = len(frame)
print (width, height)

while(True):

    #img = np.copy(frame)

    img = cv2.resize(frame, (int(width/3), int(height/3)))

    for x in range(1, Config.dilate_iterations):
        img = cv2.erode(img, Config.kernel)

    for x in range(1, Config.dilate_iterations):
        img = cv2.dilate(img, Config.kernel)

    detector = cv2.SimpleBlobDetector_create(blob_params)
    keypoints = detector.detect(img)
    img = cv2.drawKeypoints(
        img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("window1", img)

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

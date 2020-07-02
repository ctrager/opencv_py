import glob
import cv2
import sys

root_dir = "//home/corey/Downloads/record/"

#e	preferred Capture API backends to use. Can be used to enforce a specific reader implementation if multiple are available: e.g. 
#cv::CAP_FFMPEG or cv::CAP_IMAGES or cv::CAP_DSHOW.

for filename in glob.iglob(root_dir + '**/*.mp4', recursive=True):
    print(filename)
    video_capture = cv2.VideoCapture(filename)
    # print(video_capture.isOpened())
    
    while video_capture.isOpened() == True:
        ret, frame = video_capture.read()
        if ret == True:
            #print(len(frame))
            small = cv2.resize(frame,(300,200))
            cv2.imshow("window1", small)
    
            key = cv2.waitKey(1) 

            if key == 27: # escape key
                break

            if cv2.getWindowProperty("window1",cv2.WND_PROP_AUTOSIZE)  < 1: # closed with X       
                break  

            ret, frame = video_capture.read()
        else:
            break
        
    video_capture.release()
    #sys.exit()

cv2.destroyAllWindows()

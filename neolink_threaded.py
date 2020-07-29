import numpy as np
import cv2
import time
import threading

class Config:
    url = "rtsp://10.0.0.8:8554/one"
#    url = "rtsp://127.0.0.1:8554/one"
    framerate = 12
    queue_size = framerate * 50
    gauss_blur = 5
    interval_in_milliseconds = 0
    motion_threshold_percent = 30
    recording_length_in_seconds = 15
    cooldown_in_seconds = 12
    create_video = 0
    width = 2304  # 576 768 1152
    height = 1296  # 324  432  648
    crop_y1 = 0
    crop_y2 = 960
    crop_x1 = 495
    crop_x2 = 1425
    new_size_for_video = (1152,648) 
    new_size_for_display = (768, 432)
    kernel = np.ones((5,5),np.uint8)
    rect_left = 0
    rect_top = 120
    rect_right = 768
    rect_bottom = 432

queue = []
video_capture = None
lock = threading.Lock()
stopping = False
font = cv2.FONT_HERSHEY_SIMPLEX

def append_to_queue(queue, item):
    lock.acquire()
    queue.append(item)
    lock.release()

def pop_from_queue(queue):
    lock.acquire()
    item = queue.pop(0)
    lock.release()
    return item

def queue_len(queue):
    lock.acquire()
    size = len(queue)
    lock.release()
    return size

def read_feed():    
    producer_cnt = 0
    frame = video_capture.grab()
    while (True):
        if stopping == True:
            break
        frame = video_capture.grab()
        if frame != None:
            append_to_queue(queue, frame)
    print("exiting read_feed thread")
 
#start
video_capture = cv2.VideoCapture(Config.url)
read_feed_thread = threading.Thread(target=read_feed, args=())
read_feed_thread.start()
prev_frame = []
diff_frame = []
motion_percent = 0
state = ""

consumer_cnt = 0


while(True):
    while (True):
        if queue_len(queue) > 0:
            frame = pop_from_queue(queue)
            ret,decoded = video_capture.retrieve(frame)
            if ret == False:
                print("skipping frame")
                continue
            break
        else:
            time.sleep(.04)
    consumer_cnt += 1
    
    resized_for_display = cv2.resize(decoded, Config.new_size_for_display)

    if consumer_cnt % 5 == 0:
        cropped = resized_for_display[Config.rect_top:Config.rect_bottom, Config.rect_left:Config.rect_right]
        blur_frame  = cv2.GaussianBlur(cropped, (Config.gauss_blur, Config.gauss_blur), cv2.BORDER_CONSTANT)
        eroded = cv2.erode(blur_frame, Config.kernel)
        dilated = cv2.dilate(eroded, Config.kernel)
        gray = cv2.cvtColor(dilated, cv2.COLOR_BGR2GRAY)
        diff_frame = gray
        if len(prev_frame) == 0:
            prev_frame = diff_frame

        # # how much has changed
        try:
            diff = cv2.absdiff(diff_frame, prev_frame)
            sum_diff = np.sum(diff, dtype=np.int64)
            sum_prev_frame = np.sum(prev_frame, dtype=np.int64)
            pct = sum_diff/sum_prev_frame * 5
            motion_percent = int(round(pct * 100))
        except:
            motion_percent = 0            

        # calc score here


        #cv2.imshow("d", gray)
    
    # text on image
    text_on_image = str(motion_percent) # + "," + state + "," + str(fps)
    cv2.putText(resized_for_display, text_on_image,
         (10, len(resized_for_display) - 20  ), font, 
         .8, (255,255,0), 2, cv2.LINE_AA)

    cv2.imshow("window1", resized_for_display)

    # detect window closing
    key = cv2.waitKey(1) 

    if key == 27: # escape key
        break

    if cv2.getWindowProperty("window1",cv2.WND_PROP_AUTOSIZE)  < 1: # closed with X       
        break   

    prev_frame = diff_frame

# clean up
print("clean up")
stopping = True
read_feed_thread.join()
video_capture.release()
cv2.destroyAllWindows()
print("goodbye")

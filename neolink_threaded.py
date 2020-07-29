import numpy as np
import cv2
import time
import threading

class Config:
    url = "rtsp://10.0.0.8:8554/one"
#    url = "rtsp://127.0.0.1:8554/one"
    framerate = 12
    queue_size = 36
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

lock =threading.Lock()

video_capture = cv2.VideoCapture(Config.url)

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


def thread_func():    
    producer_cnt = 0
    frame = video_capture.grab()
    while (True):
        frame = video_capture.grab()
        if frame != None:
            producer_cnt += 1
            if queue_len(queue) > Config.queue_size:
                pop_from_queue(queue)
            
            append_to_queue(queue, frame)
            print("producer", producer_cnt)
 

mythread = threading.Thread(target=thread_func, args=())
mythread.start()

consumer_cnt = 0
while(True):
    while (True):
        if queue_len(queue) > 0:
            frame = pop_from_queue(queue)
            break
        else:
            time.sleep(.1)
    consumer_cnt += 1
    ret,decoded = video_capture.retrieve(frame)
    resized = cv2.resize(decoded, Config.new_size_for_display)
    cv2.imshow("w",resized)
    cv2.waitKey(1)
    print("consumer", consumer_cnt, np.sum(decoded, dtype=np.int64))
    #time.sleep(.2)
print("goodbye")

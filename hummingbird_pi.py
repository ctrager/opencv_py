
import numpy as np
import cv2
import time

# color calculator
# https://alloyui.com/examples/color-picker/hsv.html
class Config:
    gauss_blur = 5
    screen_scale_factor = .2
    queue_size = 72
    interval_in_milliseconds = 400
    motion_threshold_percent = 20
    recording_length_in_seconds = 12
    cooldown_in_seconds = 12
    framerate = 15
    create_video = 0
    width = 1920
    height = 1080
    crop_y1 = 0
    crop_y2 = 960
    crop_x1 = 495
    crop_x2 = 1425
    # new size is 930 X 960
    new_size_for_analysis = (310,320) # 1/3 size
    new_size_for_video = (960,540) 
    new_size_for_display = (640, 360)
    #rect_points = ((60,100),(134,280),(186,100),(260,280))
    rect_points = ((95,45),(280,265))
    kernel = np.ones((5,5),np.uint8)

BLUE = 0
GREEN = 1
RED = 2
ORIGINAL_FRAME = 0
DIFF_FRAME = 1
STATE_NONE = "none"
STATE_RECORDING = "recording"
STATE_COOLDOWN = "cooldown"

state = STATE_NONE
state_start_time = 0

prev_frame = []

fourcc = cv2.VideoWriter_fourcc(*'avc1')
font = cv2.FONT_HERSHEY_SIMPLEX
motion_percent = 0

def prep_frame_for_video(frame):
    img = cv2.resize(frame, Config.new_size_for_video)
    return img

def current_milliseconds():
    return round(time.time() * 1000)

def change_state(new_state):
    global state
    global state_start_time
    now_string = time.strftime("%Y-%m-%d %H:%M:%S")  
    state = new_state
    state_start_time = current_milliseconds()
    print(now_string, "state", state, new_state)

def start_video():
    video_capture = cv2.VideoCapture(
       "rtsp://10.0.0.15:8554/unicast")
#        "http://127.0.0.1:8080/")
    return video_capture

def process_frame(frame):
    
    # resize
    small_frame = cv2.resize(frame, Config.new_size_for_display)

    blur_frame  = cv2.GaussianBlur(small_frame,
        (Config.gauss_blur, Config.gauss_blur), cv2.BORDER_CONSTANT)

    eroded = cv2.erode(blur_frame, Config.kernel)
    dilated = cv2.dilate(eroded, Config.kernel)

    
    top_left = Config.rect_points[0]
    bottom_right = Config.rect_points[1]
    cropped = dilated[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    
    cv2.imshow("d", cropped)
    return [small_frame, cropped]


# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

def handle_gauss_blur(arg1):
    Config.gauss_blur = arg1
    if Config.gauss_blur % 2 == 0:
        Config.gauss_blur = Config.gauss_blur + 1
cv2.createTrackbar("blur", "window1", 0, 20, handle_gauss_blur)
cv2.setTrackbarPos("blur", "window1", Config.gauss_blur)

def handle_create_video(arg1):
    Config.create_video = arg1
cv2.createTrackbar("create_video", "window1", 0, 1, handle_create_video)
cv2.setTrackbarPos("create_video", "window1", Config.create_video)

def handle_motion_threshold_percent(arg1):
    Config.motion_threshold_percent = arg1
cv2.createTrackbar("motion_threshold_percent", "window1", 0, 50, handle_motion_threshold_percent)
cv2.setTrackbarPos("motion_threshold_percent", "window1", Config.motion_threshold_percent)

#video_capture = cv2.VideoCapture(0)
video_capture = start_video()

# get first frame
ret = False
frame = None

ret, frame = video_capture.read()
print(len([frame][0][0]), len(frame))
prev_frame = process_frame(frame)[DIFF_FRAME]

prev_time = current_milliseconds()
start_time = prev_time
frame_count = 0
fps = 0
motion_percent = 0
 
queue = []

while(True):
    frame_count += 1

    now = current_milliseconds()

    frames = process_frame(frame)
    orig = frames[ORIGINAL_FRAME]
    curr_frame = frames[DIFF_FRAME]
    
    if now - prev_time > Config.interval_in_milliseconds:
        elapsed_seconds = (now - start_time)/1000
        fps = round(frame_count/elapsed_seconds)
      
        # # how much has changed
        diff = cv2.absdiff(curr_frame, prev_frame)
        sum_diff = np.sum(diff, dtype=np.int64)
        sum_curr_frame = np.sum(curr_frame, dtype=np.int64)
        sum_prev_frame = np.sum(prev_frame)
        pct = sum_diff/sum_prev_frame * 3
        motion_percent = int(round(pct * 100))
        #print(sum_diff)
        if state == STATE_NONE:
            if motion_percent > Config.motion_threshold_percent:
                change_state(STATE_RECORDING)
                if Config.create_video == 1:
                    filename =  "./videos/hum_" \
                        + time.strftime("%Y-%m-%d-%H-%M-%S") \
                        + "_pct" + str(motion_percent) + ".mp4"
                    print(filename)
                    video_file = cv2.VideoWriter(filename, fourcc, Config.framerate, 
                        Config.new_size_for_video)
                    # print a couple seconds ago
                    for item in queue:
                        past_frame = prep_frame_for_video(item[0])
                        video_file.write(past_frame)

        prev_frame = curr_frame
        prev_time = now

    # text on image
    text_on_image = str(motion_percent)+ "," + state + "," + str(fps)
    cv2.putText(orig, text_on_image,
         (10, len(orig) - 20  ), font, 
         .8, (255,255,0), 2, cv2.LINE_AA)

    # rectange on image    
    top_left = Config.rect_points[0]
    bottom_right = Config.rect_points[1]
    cv2.rectangle(orig, top_left, bottom_right, (255,255,0), 1)

    display_image = np.hstack([
        orig
    ])

    cv2.imshow('window1',display_image)

    if state == STATE_RECORDING:
        if now - state_start_time > (Config.recording_length_in_seconds * 1000):
            # finish recording
            if Config.create_video == 1:
                video_file.release()
            change_state(STATE_COOLDOWN)
        else:
            # continue recording
            frame_for_video = prep_frame_for_video(frame)
            if Config.create_video == 1:
                video_file.write(frame_for_video)
    
    elif state == STATE_COOLDOWN:
        if now - state_start_time > (Config.cooldown_in_seconds * 1000):
            change_state(STATE_NONE)

    if state == STATE_NONE or state == STATE_COOLDOWN:
        if len(queue) >= Config.queue_size:
            queue.pop(0)
        if len(queue) < Config.queue_size:
            queue.append([frame,motion_percent])

    # detect window closing
    key = cv2.waitKey(1) 

    if key == 27: # escape key
        break

    if cv2.getWindowProperty("window1",cv2.WND_PROP_AUTOSIZE)  < 1: # closed with X       
        break   
  
    # get next frame
    ret = False
    while(ret == False):
        try:
            ret, frame = video_capture.read()
            if (ret == False):
                print(time.strftime("%Y-%m-%d %H:%M:%S"))
                print("reading frame returned false")
                time.sleep(1)
                try:
                    video_capture.release()
                except:
                    print("releasing video threw exception")
                video_capture = start_video()
        except:
            print(time.strftime("%Y-%m-%d %H:%M:%S"))
            print("reading frame threw exception")
            time.sleep(1)
  
# clean up
video_capture.release()
cv2.destroyAllWindows()

print("goodbye")

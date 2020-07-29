
import numpy as np
import cv2
import time
class Config:
#    url = "rtsp://10.0.0.8:8554/one"
    url = "rtsp://127.0.0.1:8554/one"
    gauss_blur = 5
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


STATE_NONE = "none"
STATE_RECORDING = "recording"
STATE_COOLDOWN = "cooldown"

state = STATE_NONE
state_start_time = 0

fourcc = cv2.VideoWriter_fourcc(*'avc1')
font = cv2.FONT_HERSHEY_SIMPLEX
motion_percent = 0
frame_count = 0
fps = 0
 
queue = []

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
    video_capture = cv2.VideoCapture(Config.url)
    return video_capture

# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

def handle_gauss_blur(arg1):
    Config.gauss_blur = arg1
    if Config.gauss_blur % 2 == 0:
        Config.gauss_blur = Config.gauss_blur + 1
#cv2.createTrackbar("blur", "window1", 0, 20, handle_gauss_blur)
#cv2.setTrackbarPos("blur", "window1", Config.gauss_blur)

def handle_create_video(arg1):
    Config.create_video = arg1
cv2.createTrackbar("create_video", "window1", 0, 1, handle_create_video)
cv2.setTrackbarPos("create_video", "window1", Config.create_video)

def handle_motion_threshold_percent(arg1):
    Config.motion_threshold_percent = arg1
cv2.createTrackbar("motion_threshold_percent", "window1", 0, 50, handle_motion_threshold_percent)
cv2.setTrackbarPos("motion_threshold_percent", "window1", Config.motion_threshold_percent)

def handle_left(arg1):
    Config.rect_left = arg1
cv2.createTrackbar("left", "window1", 0, Config.new_size_for_display[0], handle_left)
cv2.setTrackbarPos("left", "window1", Config.rect_left)

def handle_top(arg1):
    Config.rect_top = arg1
cv2.createTrackbar("top", "window1", 0, Config.new_size_for_display[1], handle_top)
cv2.setTrackbarPos("top", "window1", Config.rect_top)

def handle_right(arg1):
    Config.rect_right = arg1
cv2.createTrackbar("right", "window1", 0, Config.new_size_for_display[0], handle_right)
cv2.setTrackbarPos("right", "window1", Config.rect_right)

def handle_bottom(arg1):
    Config.rect_bottom = arg1
cv2.createTrackbar("bottom", "window1", 0, Config.new_size_for_display[1], handle_bottom)
cv2.setTrackbarPos("bottom", "window1", Config.rect_bottom)

video_capture = start_video()

def process_frame(frame, do_all):
    
    # resize
    small_frame = cv2.resize(frame, Config.new_size_for_display)

    if do_all:
        cropped = small_frame[Config.rect_top:Config.rect_bottom, Config.rect_left:Config.rect_right]

        blur_frame  = cv2.GaussianBlur(cropped,
            (Config.gauss_blur, Config.gauss_blur), cv2.BORDER_CONSTANT)

        eroded = cv2.erode(blur_frame, Config.kernel)
        dilated = cv2.dilate(eroded, Config.kernel)

        gray = cv2.cvtColor(dilated, cv2.COLOR_BGR2GRAY)

        cv2.imshow("d", gray)
        return [small_frame, gray]
    else:
        return [small_frame]

ret, frame = video_capture.read()
print(len([frame][0][0]), len(frame))
prev_frame = process_frame(frame, True)[1]

prev_time = current_milliseconds()
start_time = prev_time

while(True):
    frame_count += 1

    now = current_milliseconds()
   
    if now - prev_time > Config.interval_in_milliseconds:
        frames = process_frame(frame, True)
        elapsed_seconds = (now - start_time)/1000
        fps = round(frame_count/elapsed_seconds)
      
        # # how much has changed
        try:
            diff = cv2.absdiff(frames[1], prev_frame)
            sum_diff = np.sum(diff, dtype=np.int64)
            sum_prev_frame = np.sum(prev_frame, dtype=np.int64)
            pct = sum_diff/sum_prev_frame * 5
            motion_percent = int(round(pct * 100))
        except:
            motion_percent = 0

        if state == STATE_NONE:
            if motion_percent > Config.motion_threshold_percent:
                change_state(STATE_RECORDING)
                if Config.create_video == 1:
                    filename =  "./videos/neo_" \
                        + time.strftime("%Y-%m-%d-%H-%M-%S") \
                        + "_pct" + str(motion_percent) + ".mp4"
                    print(filename)
                    video_file = cv2.VideoWriter(filename, fourcc, Config.framerate, 
                        Config.new_size_for_video)
                    # print a couple seconds ago
                    for item in queue:
                        video_file.write(item)
                    queue.clear()    

        prev_frame = frames[1]
        prev_time = now
    else:
        frames = process_frame(frame, False)

    # text on image
    text_on_image = str(motion_percent)+ "," + state + "," + str(fps)
    cv2.putText(frames[0], text_on_image,
         (10, len(frames[0]) - 20  ), font, 
         .8, (255,255,0), 2, cv2.LINE_AA)

    # rectange on image    
    top_left = (Config.rect_left, Config.rect_top)
    bottom_right = (Config.rect_right, Config.rect_bottom)
    cv2.rectangle(frames[0], top_left, bottom_right, (255,255,0), 1)

    display_image = np.hstack([
        frames[0]
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
            frame_sized_for_video = cv2.resize(frame, Config.new_size_for_video)
            if Config.create_video == 1:
                video_file.write(frame_sized_for_video)
    
    elif state == STATE_COOLDOWN:
        if now - state_start_time > (Config.cooldown_in_seconds * 1000):
            change_state(STATE_NONE)

    if state == STATE_NONE or state == STATE_COOLDOWN:
        if len(queue) >= Config.queue_size:
            queue.pop(0)
        if len(queue) < Config.queue_size:
            frame_sized_for_video = cv2.resize(frame, Config.new_size_for_video)
            queue.append(frame_sized_for_video)

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
                time.sleep(0.05)
                try:
                    video_capture.release()
                except:
                    print("releasing video threw exception")
                video_capture = start_video()
        except:
            print(time.strftime("%Y-%m-%d %H:%M:%S"))
            print("reading frame threw exception")
            time.sleep(0.05)
  
# clean up
video_capture.release()
cv2.destroyAllWindows()

print("goodbye")

import numpy as np
import cv2
import time

# color calculator
# https://alloyui.com/examples/color-picker/hsv.html
class Config:
    gauss_blur = 9
    screen_scale_factor = .2
    # 0-255
    red_lightness = 50
    red_saturation = 50
    yellow_lightness = 50
    yellow_saturation = 50
    blue_lightness = 50
    blue_saturation = 50
    red1 = (170,180)
    red2 = (0, 10)
    yellow = (25,32)
    blue = (105, 135)
    interval_in_milliseconds = 400
    motion_threshold_percent = 20
    recording_length_in_seconds = 8
    cooldown_in_seconds = 12
    framerate = 24
    create_video = 0
    width = 1920
    height = 1080
    crop_y1 = 0
    crop_y2 = 960
    crop_x1 = 495
    crop_x2 = 1425
    # new size is 930 X 960
    new_size_for_analysis = (310,320) # 1/3 size
    new_size_for_video = (620,640) # 2/3 size
    #rect_points = ((60,100),(134,280),(186,100),(260,280))
    rect_points = ((60,60),(260,290))
    kernel = np.ones((3,3),np.uint8)

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
    img = frame[Config.crop_y1:Config.crop_y2, Config.crop_x1:Config.crop_x2]
    img = cv2.resize(img, Config.new_size_for_video)
    return img

def prep_frame_for_analysis(frame):
    img = frame[Config.crop_y1:Config.crop_y2, Config.crop_x1:Config.crop_x2]
    img = cv2.resize(img, Config.new_size_for_analysis)
    return img

def handle_gauss_blur(arg1):
    Config.gauss_blur = arg1
    if Config.gauss_blur % 2 == 0:
        Config.gauss_blur = Config.gauss_blur + 1

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
        "rtsp://admin:password1@10.0.0.7:554/cam/realmonitor?channel=1&subtype=0")
    return video_capture

def process_frame(frame):
    
    # resize
    small_frame = prep_frame_for_analysis(frame)

    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)

    # red crosses 0, so we need to ranges
    in_range_red1 = cv2.inRange(hsv, 
        (Config.red1[0], Config.red_saturation, Config.red_lightness), 
        (Config.red1[1], 255, 255))

    in_range_red2 = cv2.inRange(hsv, 
        (Config.red2[0], Config.red_saturation, Config.red_lightness), 
        (Config.red2[1], 255, 255))

    in_range_yellow = cv2.inRange(hsv, 
        (Config.yellow[0], Config.yellow_saturation, Config.yellow_lightness), 
        (Config.yellow[1], 255, 255))

    in_range_blue = cv2.inRange(hsv, 
        (Config.blue[0], Config.blue_saturation, Config.blue_lightness), 
        (Config.blue[1], 255, 255))

    in_range_all_gray = cv2.bitwise_or(in_range_red1, in_range_red2)
    in_range_all_gray = cv2.bitwise_or(in_range_all_gray, in_range_yellow)
    in_range_all_gray = cv2.bitwise_or(in_range_all_gray, in_range_blue)

    gray_with_holes = cv2.bitwise_and(gray, gray, mask=255-in_range_all_gray)
    gray_with_holes = cv2.cvtColor(gray_with_holes, cv2.COLOR_GRAY2BGR)

    colors_without_gray = cv2.bitwise_and(small_frame, small_frame, mask=in_range_all_gray)
    
    # both is the image with gray scale except for the colors we allow to show
    both = cv2.bitwise_or(gray_with_holes, colors_without_gray)
   
    # return an array of frames
    # "original" is index 0
    # the one for diffing is index 1
    # others appended
    # return [small_frame, colors_without_gray, both]
   
    # blur
    #colors_without_gray = cv2.GaussianBlur(colors_without_gray,
    #    (Config.gauss_blur, Config.gauss_blur), cv2.BORDER_CONSTANT)

    # colors_without_gray = cv2.erode(colors_without_gray, Config.kernel)

    #kernel = np.ones((3,3),np.uint8)
    colors_without_gray = cv2.dilate(colors_without_gray, Config.kernel)

    return [small_frame, colors_without_gray, both]

# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

def handle_create_video(arg1):
    Config.create_video = arg1
cv2.createTrackbar("create_video", "window1", 0, 1, handle_create_video)
cv2.setTrackbarPos("create_video", "window1", Config.create_video)

def handle_motion_threshold_percent(arg1):
    Config.motion_threshold_percent = arg1
cv2.createTrackbar("motion_threshold_percent", "window1", 0, 50, handle_motion_threshold_percent)
cv2.setTrackbarPos("motion_threshold_percent", "window1", Config.motion_threshold_percent)

# red
def handle_red_lightness(arg1):
    Config.red_lightness = arg1
cv2.createTrackbar("red_lightness", "window1", 0, 255, handle_red_lightness)
cv2.setTrackbarPos("red_lightness", "window1", Config.red_lightness)

def handle_red_saturation(arg1):
    Config.red_saturation = arg1
cv2.createTrackbar("red_saturation", "window1", 0, 255, handle_red_saturation)
cv2.setTrackbarPos("red_saturation", "window1", Config.red_saturation)

# blue
def handle_blue_lightness(arg1):
    Config.blue_lightness = arg1
cv2.createTrackbar("blue_lightness", "window1", 0, 255, handle_blue_lightness)
cv2.setTrackbarPos("blue_lightness", "window1", Config.blue_lightness)

def handle_blue_saturation(arg1):
    Config.blue_saturation = arg1
cv2.createTrackbar("blue_saturation", "window1", 0, 255, handle_blue_saturation)
cv2.setTrackbarPos("blue_saturation", "window1", Config.blue_saturation)

# yellow
def handle_yellow_lightness(arg1):
    Config.yellow_lightness = arg1
cv2.createTrackbar("yellow_lightness", "window1", 0, 255, handle_yellow_lightness)
cv2.setTrackbarPos("yellow_lightness", "window1", Config.yellow_lightness)

def handle_yellow_saturation(arg1):
    Config.yellow_saturation = arg1
cv2.createTrackbar("yellow_saturation", "window1", 0, 255, handle_yellow_saturation)
cv2.setTrackbarPos("yellow_saturation", "window1", Config.yellow_saturation)

#video_capture = cv2.VideoCapture(0)
video_capture = start_video()

# get first frame
ret, frame = video_capture.read()

top_left = Config.rect_points[0]
bottom_right = Config.rect_points[1]
pixel_count = (bottom_right[0] - top_left[0]) * (bottom_right[1] - top_left[1])

prev_frame = process_frame(frame)[DIFF_FRAME]
prev_frame = prev_frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

def calc_hist(img):
    b = cv2.calcHist(img, [0], None, [24], [0,256])
    g = cv2.calcHist(img, [1], None, [24], [0,256])
    r = cv2.calcHist(img, [2], None, [24], [0,256])
    return np.array([b,g,r])

prev_hist = calc_hist(prev_frame)

# just for display purposes
delta_bgr = prev_frame

prev_time = current_milliseconds()
start_time = prev_time
frame_count = 0
fps = 0
 
queue = []

while(True):
    frame_count += 1

    now = current_milliseconds()

    altered_frames = process_frame(frame)
    orig = altered_frames[ORIGINAL_FRAME]

    if now - prev_time > Config.interval_in_milliseconds:
        elapsed_seconds = (now - start_time)/1000
        fps = round(frame_count/elapsed_seconds)
      
        # how much has changed

        top_left = Config.rect_points[0]
        bottom_right = Config.rect_points[1]
        curr_frame = altered_frames[DIFF_FRAME][top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    
        curr_hist = calc_hist(curr_frame)

        diff = cv2.absdiff(curr_hist, prev_hist)
        diff_sum = np.sum(diff)
        prev_sum = np.sum(prev_hist)

        motion_percent = int(round((diff_sum/prev_sum) * 100))
     
        if state == STATE_NONE:
            if motion_percent > Config.motion_threshold_percent:
                change_state(STATE_RECORDING)
                if Config.create_video == 1:
                    filename =  "./videos/video_" \
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
        prev_hist = curr_hist
        prev_time = now

    # text on image
    text_on_image = str(motion_percent) + "," + state + "," + str(fps)
    cv2.putText(orig, text_on_image,
        (10, len(orig) - 20  ), font, 
        .8, (255,255,0), 2, cv2.LINE_AA)

    # rectange on image    
    top_left = Config.rect_points[0]
    bottom_right = Config.rect_points[1]
    cv2.rectangle(altered_frames[2], top_left, bottom_right, (255,255,0), 1)
 
    padded_frame = cv2.copyMakeBorder(prev_frame, 
        0, len(orig) - len(prev_frame), 0, len(orig[0]) - len(prev_frame[0]), cv2.BORDER_CONSTANT, value=(127,127,127))
    
    display_image = np.hstack([
        orig, 
        altered_frames[2],
        padded_frame
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
        if len(queue) >= 60:
            queue.pop(0)
        if len(queue) < 60:
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

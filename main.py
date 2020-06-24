import numpy as np
import cv2
import time

class Config:
    gauss_blur = 25
    screen_scale_factor = .2
    new_size = [0,0]
    pixel_count = 0
    lightness = 40
    saturation = 100
    yellow_green = 15
    blue_green = 100
    interval_in_milliseconds = 400
    motion_threshold_percent = 4
    recording_length_in_seconds = 8
    cooldown_in_seconds = 10
    framerate = 20
    create_video = 1

BLUE = 0
GREEN = 1
RED = 2
ORIGINAL_FRAME = 0
DIFF_FRAME = 1
STATE_NONE = "none"
STATE_RECORDING = "recording"

state = STATE_NONE

def handle_gauss_blur(arg1):
    Config.gauss_blur = arg1
    if Config.gauss_blur % 2 == 0:
        Config.gauss_blur = Config.gauss_blur + 1

def handle_lightness(arg1):
    Config.lightness = arg1

def handle_saturation(arg1):
    Config.saturation = arg1

def handle_yellow_green(arg1):
    Config.yellow_green = arg1

def handle_blue_green(arg1):
    Config.blue_green = arg1

def handle_motion_threshold_percent(arg1):
    Config.motion_threshold_percent = arg1

def handle_create_video(arg1):
    Config.create_video = arg1

def current_milliseconds():
    return round(time.time() * 1000)

def change_state(new_state):
    global state
    now = time.strftime("%Y-%m-%d %H:%M:%S")  
    print(now, "state", state, new_state)
    state = new_state

def get_filename():
    return "./videos/video_" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".mp4"

def prep_frame_for_analysis(frame):
    return prep_frame_for_video(frame)

def prep_frame_for_video(frame):
    img = frame[0:900, 500:1420]
    # now its 920 x 900
    img = cv2.resize(img, (460,450))
    return img

def process_frame(frame):
    
    # resize
    small_frame = prep_frame_for_analysis(frame)
    
    # blur
    blurred_frame = cv2.GaussianBlur(small_frame,
        (Config.gauss_blur, Config.gauss_blur), cv2.BORDER_CONSTANT)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    # red to yellow, but not into green
    in_range1 = cv2.inRange(hsv, 
        (0, Config.saturation, Config.lightness), 
        (Config.yellow_green, 255, 255))
    
    # red to maybe turqoise, but not into green
    in_range2 = cv2.inRange(hsv, 
        (Config.blue_green, Config.saturation, Config.lightness), 
        (180, 255, 255))

    in_range_all_gray = cv2.bitwise_or(in_range1, in_range2)

    # return an array of frames
    # "original" is index 0
    # the one for diffing is index 1
    # others appended
    return [small_frame, in_range_all_gray]

prev_frame = []

# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar("create_video", "window1", 0, 1, handle_create_video)
cv2.createTrackbar("motion_threshold_percent", "window1", 0, 255, handle_motion_threshold_percent)
cv2.createTrackbar("lightness", "window1", 0, 255, handle_lightness)
cv2.createTrackbar("saturation", "window1", 0, 255, handle_saturation)
cv2.createTrackbar("yellow_green", "window1", 0, 255, handle_yellow_green)
cv2.createTrackbar("blue_green", "window1", 0, 255, handle_blue_green)

cv2.setTrackbarPos("create_video", "window1", Config.create_video)
cv2.setTrackbarPos("motion_threshold_percent", "window1", Config.motion_threshold_percent)
cv2.setTrackbarPos("lightness", "window1", Config.lightness)
cv2.setTrackbarPos("saturation", "window1", Config.saturation)
cv2.setTrackbarPos("yellow_green", "window1", Config.yellow_green)
cv2.setTrackbarPos("blue_green", "window1", Config.blue_green)

#video_capture = cv2.VideoCapture(0)
video_capture = cv2.VideoCapture(
    "rtsp://admin:password1@10.0.0.7:554/cam/realmonitor?channel=1&subtype=0")

# get first frame
ret, frame = video_capture.read()

# for scaling
width = len(frame[0])
height = len(frame)
print (width, height)

Config.new_size = (int(width * Config.screen_scale_factor), int(height * Config.screen_scale_factor))
Config.pixel_count = Config.new_size[0] * Config.new_size[1]

prev_frame = process_frame(frame)[DIFF_FRAME]
delta_frame_gray = prev_frame

prev_time = current_milliseconds()

recording_start_time = 0

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
font = cv2.FONT_HERSHEY_SIMPLEX
motion_percent = 0

while(True):

    now = current_milliseconds()

    altered_frames = process_frame(frame)

    if now - prev_time > Config.interval_in_milliseconds:
        # how much has changed
  
        delta_frame_gray = cv2.absdiff(altered_frames[DIFF_FRAME], prev_frame)
        pixels_with_motion_count = cv2.countNonZero(delta_frame_gray)

        motion_percent = round(pixels_with_motion_count/Config.pixel_count * 100)
  
        if state == STATE_NONE:
            if Config.create_video == 1 and motion_percent > Config.motion_threshold_percent:
                change_state(STATE_RECORDING)
                recording_start_time = now
                video_file = cv2.VideoWriter(get_filename(), fourcc, Config.framerate, (width, height))

        prev_frame = altered_frames[DIFF_FRAME]
        prev_time = now

    cv2.putText(altered_frames[ORIGINAL_FRAME], state + ":" + str(motion_percent), 
        (10, len(altered_frames[ORIGINAL_FRAME]) - 20  ), font, .5, (255,255,0), 1, cv2.LINE_AA)
    
    display_image = np.hstack([
        altered_frames[ORIGINAL_FRAME], 
        # cv2.cvtColor(altered_frames[DIFF_FRAME], cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(delta_frame_gray, cv2.COLOR_GRAY2BGR)])

    cv2.imshow('window1',display_image)

    if state == STATE_RECORDING:

        if now - recording_start_time > (Config.recording_length_in_seconds * 1000):
            # finish recording
            video_file.release()
            change_state(STATE_NONE)
        else:
            # continue recording
            frame_for_video = prep_frame_for_video(frame)
            video_file.write(frame_for_video)
         

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

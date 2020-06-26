import numpy as np
import cv2
import time

#todo
# cooldown
# better configurability
# detection regions
# experiments with 
# https://stackoverflow.com/questions/189943/how-can-i-quantify-difference-between-two-images
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_video/py_lucas_kanade/py_lucas_kanade.html

# color calculator
# https://alloyui.com/examples/color-picker/hsv.html
class Config:
    gauss_blur = 3
    screen_scale_factor = .2
    pixel_count = 0
    # 0-255
    lightness = 50
    saturation = 50
    yellow_green = 10
    blue_green = 160
    interval_in_milliseconds = 400
    motion_threshold_percent = 20
    recording_length_in_seconds = 8
    cooldown_in_seconds = 12
    framerate = 24
    create_video = 1
    width = 1920
    height = 1080
    crop_y1 = 0
    crop_y2 = 900
    crop_x1 = 495
    crop_x2 = 1425
    # new size is 930 X 900
    new_size_for_analysis = (310,300) # 1/3 size
    new_size_for_video = (620,600) # 2/2 size
    pixel_count = 310 * 300

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

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
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
    global state_start_time
    now_string = time.strftime("%Y-%m-%d %H:%M:%S")  
    state = new_state
    state_start_time = current_milliseconds()
    print(now_string, "state", state, new_state)

def process_frame(frame):
    
    # resize
    small_frame = prep_frame_for_analysis(frame)

    # blur
    blurred_frame = cv2.GaussianBlur(small_frame,
        (Config.gauss_blur, Config.gauss_blur), cv2.BORDER_CONSTANT)

    gray = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2GRAY)

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

    gray_without_red = cv2.bitwise_and(gray, gray, mask=255-in_range_all_gray)
    gray_without_red_bgr = cv2.cvtColor(gray_without_red, cv2.COLOR_GRAY2BGR)

    just_red = cv2.bitwise_and(small_frame, small_frame, mask=in_range_all_gray)
    
    both = cv2.bitwise_or(gray_without_red_bgr, just_red)


    # return an array of frames
    # "original" is index 0
    # the one for diffing is index 1
    # others appended
    return [small_frame, just_red, both]


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

prev_frame = process_frame(frame)[DIFF_FRAME]
delta_frame = prev_frame
delta_bgr = prev_frame

prev_time = current_milliseconds()

while(True):

    now = current_milliseconds()

    altered_frames = process_frame(frame)

    if now - prev_time > Config.interval_in_milliseconds:
        # how much has changed
  
        delta_bgr = cv2.absdiff(altered_frames[DIFF_FRAME], prev_frame)
        delta_gray = cv2.cvtColor(delta_bgr, cv2.COLOR_BGR2GRAY)
        pixels_with_motion_count = cv2.countNonZero(delta_gray)

        motion_percent = round(pixels_with_motion_count/Config.pixel_count * 100)
  
        if state == STATE_NONE:
            if Config.create_video == 1 and motion_percent > Config.motion_threshold_percent:
                change_state(STATE_RECORDING)
                filename =  "./videos/video_" \
                    + time.strftime("%Y-%m-%d-%H-%M-%S") \
                    + "_pct" + str(motion_percent) + ".mp4"

                video_file = cv2.VideoWriter(filename, fourcc, Config.framerate, 
                    Config.new_size_for_video)

        prev_frame = altered_frames[DIFF_FRAME]
        prev_time = now

    cv2.putText(altered_frames[ORIGINAL_FRAME], state + ":" + str(motion_percent), 
        (10, len(altered_frames[ORIGINAL_FRAME]) - 20  ), font, .8, (255,255,0), 2, cv2.LINE_AA)
    
    display_image = np.hstack([
        altered_frames[ORIGINAL_FRAME], 
        altered_frames[2],
        delta_bgr])

    cv2.imshow('window1',display_image)

    if state == STATE_RECORDING:
        if now - state_start_time > (Config.recording_length_in_seconds * 1000):
            # finish recording
            video_file.release()
            change_state(STATE_COOLDOWN)
        else:
            # continue recording
            frame_for_video = prep_frame_for_video(frame)
            video_file.write(frame_for_video)
    
    elif state == STATE_COOLDOWN:
        if now - state_start_time > (Config.cooldown_in_seconds * 1000):
            change_state(STATE_NONE)

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

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
    # 0-255
    lightness = 50
    saturation = 50
    interval_in_milliseconds = 400
    motion_threshold_percent = 20
    recording_length_in_seconds = 8
    cooldown_in_seconds = 12
    framerate = 24
    create_video = 0
    width = 1920
    height = 1080
    crop_y1 = 0
    crop_y2 = 900
    crop_x1 = 200
    crop_x2 = 1500
    # new size is 1500 x 900
    new_size_for_analysis = (325,225) 
    new_size_for_video = (975,675) 
    rect_points = ((40,90),(110,200),(200,80),(280,200))

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

    gray_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2GRAY)
    gray_frame_bgr = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
    
    upper_left = Config.rect_points[0]
    bottom_right = Config.rect_points[1]
    cv2.rectangle(small_frame, upper_left, bottom_right, (255,255,0), 1)
    upper_left = Config.rect_points[2]
    bottom_right = Config.rect_points[3]
    cv2.rectangle(small_frame, upper_left, bottom_right, (255,255,0), 1)
 
    return [small_frame, gray_frame, gray_frame_bgr]


# build windows
cv2.namedWindow("window1", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar("create_video", "window1", 0, 1, handle_create_video)
cv2.createTrackbar("motion_threshold_percent", "window1", 0, 50, handle_motion_threshold_percent)

cv2.setTrackbarPos("create_video", "window1", Config.create_video)
cv2.setTrackbarPos("motion_threshold_percent", "window1", Config.motion_threshold_percent)

#video_capture = cv2.VideoCapture(0)
video_capture = cv2.VideoCapture(
    "rtsp://corey:password1@10.0.0.9/live")

# get first frame
ret, frame = video_capture.read()

# for scaling
width = len(frame[0])
height = len(frame)
print (width, height)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 98]
prev_frame = process_frame(frame)[DIFF_FRAME]
delta_frame = prev_frame
delta_gray = prev_frame

prev_time = current_milliseconds()

def measure_motion(upper_left, lower_right, curr, prev):
   
    ret, prev_jpg = cv2.imencode('.jpg', 
        prev[upper_left[1]:lower_right[1], upper_left[0]:lower_right[0]])
    
    ret, curr_jpg = cv2.imencode('.jpg', 
        curr[upper_left[1]:lower_right[1], upper_left[0]:lower_right[0]])

    motion_score = abs(len(curr_jpg) - len(prev_jpg))
    pixel_count = (upper_left[0]-lower_right[0]) * (upper_left[1]-lower_right[1])
    print("ms", motion_score, pixel_count, upper_left, lower_right)
    return motion_score, pixel_count

while(True):

    now = current_milliseconds()

    altered_frames = process_frame(frame)

    if now - prev_time > Config.interval_in_milliseconds:
        # how much has changed
        motion_score_1, pixel_count_1 = measure_motion(
            Config.rect_points[0], Config.rect_points[1], altered_frames[DIFF_FRAME], prev_frame)
        motion_score_2, pixel_count_2 = measure_motion(
            Config.rect_points[2], Config.rect_points[3], altered_frames[DIFF_FRAME], prev_frame)
       
        motion_score = motion_score_1 + motion_score_2
        pixel_count = pixel_count_1 + pixel_count_2
        motion_percent = round(motion_score/pixel_count * 100)
        #print(pixels_with_motion_count, motion_percent, pixel_count)
    
        if state == STATE_NONE:
            if motion_percent > Config.motion_threshold_percent:
                change_state(STATE_RECORDING)
                if Config.create_video == 1:
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
        cv2.cvtColor(prev_frame, cv2.COLOR_GRAY2BGR),
        
        cv2.cvtColor(delta_gray, cv2.COLOR_GRAY2BGR)
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

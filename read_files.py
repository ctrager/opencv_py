import glob
import cv2
import sys
import time
import numpy as np

class Config:
    width = 1920
    height = 1080
    new_size_for_analysis = (640,360)
    nth_frame = 5
    motion_percent_threshold = 30    
    back_n_frames = 20
    frames_to_write = 120
    framerate = 24
    rect_points = ((400,10), (630,300))

fourcc = cv2.VideoWriter_fourcc(*'avc1')
font = cv2.FONT_HERSHEY_SIMPLEX    

def process_frame(frame):
    small =  cv2.resize(frame, Config.new_size_for_analysis)
    top_left = Config.rect_points[0]
    bottom_right = Config.rect_points[1]
    cv2.rectangle(small, top_left, bottom_right, (255,255,0), 1)
    return small
 

def diff(curr, prev):
    diff = cv2.absdiff(curr, prev)
    diff_sum = np.sum(diff)
    prev_sum = np.sum(prev)
    pct = int(round((diff_sum/prev_sum) * 100))
    return pct

# get filenames
root_dir = "//home/corey/Downloads/record2/"

filenames = []
for filename in  glob.iglob(root_dir + '**/*.mp4', recursive=True):
    filenames.append(filename)
filenames.sort()

# init prev_frame
video_capture = cv2.VideoCapture(filenames[0])
ret, frame = video_capture.read()
frame = process_frame(frame)
prev_frame = frame
video_capture.release()

frames_with_motion = []

for filename in filenames:
    print(filename)
    video_capture = cv2.VideoCapture(filename)
    cnt = 0
    ret, frame = video_capture.read()
    
    while ret == True:
        cnt += 1

        if cnt % Config.nth_frame == 0:
            frame = process_frame(frame)
            cv2.imshow("w", frame)

            motion_percent = diff(frame, prev_frame)

            if motion_percent > Config.motion_percent_threshold:
                frame_info = {
                    "frame": frame,
                    "filename": filename,
                    "frame_number": cnt,
                    "motion_percent": motion_percent
                    }
                frames_with_motion.append(frame_info)    

            prev_frame = frame

        cv2.waitKey(1)
        
        ret, frame = video_capture.read()

    video_capture.release()

print("done with all files")

def sort_frame_info(element):
    return element["motion_percent"]

frames_with_motion.sort(reverse=True, key=sort_frame_info)

for fi in frames_with_motion[:3]:
    break  ####  SKIP WRITING
    start_frame = fi["frame_number"] - Config.back_n_frames
    if start_frame < 1:
        start_frame = 1
    filename_parts = fi["filename"].split("/")
    last_part = len(filename_parts) - 1
    filename =  "./videos/hum_" \
        + filename_parts[last_part - 2] \
        + filename_parts[last_part - 1] \
        + filename_parts[last_part] \
        + str(round(time.time() * 1000)) \
        + ".mp4"

    print(filename)
    video_file = cv2.VideoWriter(filename, fourcc, Config.framerate, 
        (Config.width, Config.height))    

    video_capture = cv2.VideoCapture(fi["filename"])
    cnt = 0
    frames_written = 0
    ret, frame = video_capture.read()
    while ret == True:
        cnt += 1
        if cnt >= start_frame and frames_written < Config.frames_to_write:
            video_file.write(frame)
            frames_written += 1
            if frames_written == Config.frames_to_write:
                break
        ret, frame = video_capture.read()
    video_file.release()
 
cv2.destroyAllWindows()

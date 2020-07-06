import glob
import cv2
import sys
import time
import numpy as np

class Config:
    width = 1920
    height = 1080
    half_width = 960
    half_height = 540
    new_size_for_analysis = (640,360)
    nth_frame = 10
    motion_percent_threshold = 26 
    back_n_frames = 30
    frames_to_write = 180
    framerate = 15
    rect_points = ((320,20), (420,190))
    root_dir = "//home/corey/Downloads/hum/"


fourcc = cv2.VideoWriter_fourcc(*'avc1')
font = cv2.FONT_HERSHEY_SIMPLEX    

def process_frame(frame):
    small =  cv2.resize(frame, Config.new_size_for_analysis)
    top_left = Config.rect_points[0]
    bottom_right = Config.rect_points[1]
    cv2.rectangle(small, top_left, bottom_right, (255,255,0), 1)
    cropped = small[20:190, 320:420]
    #rect_points = ((320,20), (420,190))

    return cropped
 

def diff(curr, prev):
    diff = cv2.absdiff(curr, prev)
    diff_sum = np.sum(diff)
    prev_sum = np.sum(prev)
    pct = int(round((diff_sum/prev_sum) * 100))
    return pct

# get filenames

filenames = []
for filename in  glob.iglob(Config.root_dir + '**/*.mp4', recursive=True):
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
    highest_score = 0
    ret, frame = video_capture.read()
    
    while ret == True:
        cnt += 1

        if cnt % Config.nth_frame == 0:
            processed_frame = process_frame(frame)

            cv2.imshow("a", processed_frame)
            cv2.waitKey(1)

            motion_percent = diff(processed_frame, prev_frame)

            if motion_percent > highest_score:
                highest_score = motion_percent
            if motion_percent > Config.motion_percent_threshold:
                frame_info = {
                    "filename": filename,
                    "frame_number": cnt,
                    "motion_percent": motion_percent
                    }
                frames_with_motion.append(frame_info) 
                print(filename, cnt, motion_percent)

            prev_frame = processed_frame
      
        ret, frame = video_capture.read()

    print("highest score", highest_score)
    video_capture.release()

print("done with analyzing files")

def sort_frame_info(element):
    return element["motion_percent"]

frames_with_motion.sort(reverse=True, key=sort_frame_info)

output_file = None
output_filename = ""

def write_clip(fi, frames_written):
    global output_file
    global output_filename

    print("write_clip", fi["filename"], fi["frame_number"], fi["motion_percent"], frames_written)

    filename_parts = fi["filename"].split("/")
    last_part = len(filename_parts) - 1
    minute = int(filename_parts[last_part][:2])
    hour = int(filename_parts[last_part - 1])
    date = filename_parts[last_part - 2]

    if frames_written > 0:
        minute += 1
        if minute == 60:
            minute = 0
            hour += 1
    
    input_filename = filename_parts[0]
    for part in filename_parts[1:len(filename_parts)-2]:
        input_filename += "/" + part
    
    input_filename += "/" + str(hour).zfill(2)
    input_filename += "/" + str(minute).zfill(2)
    input_filename += ".mp4"
 
    start_frame = 1
    if frames_written == 0:
        output_filename = "./videos/hum_" \
            + date + "_" + str(hour).zfill(2) + str(minute).zfill(2) \
            + "_" + str(fi["frame_number"]) + "_" + str(fi["motion_percent"]) + ".mp4"
        
        # open the output file
        output_file = cv2.VideoWriter(output_filename, fourcc, Config.framerate, 
            (Config.half_width, Config.half_height))    
    
        start_frame = fi["frame_number"] - Config.back_n_frames
        if start_frame < 1:
            start_frame = 1
    
    input_file = cv2.VideoCapture(input_filename)

    cnt = 0
    ret, input_frame = input_file.read()

    while ret == True:
        cnt += 1
        #cv2.imshow("b", cv2.resize(input_frame,(300,200)))
        #cv2.waitKey(1)
        if cnt >= start_frame and frames_written < Config.frames_to_write:
            half = cv2.resize(input_frame, (Config.half_width, Config.half_height))
            output_file.write(half)
            frames_written += 1
            if frames_written == Config.frames_to_write:
                break
        ret, input_frame = input_file.read()

    input_file.release()    
    
    if frames_written == Config.frames_to_write:
    #if True:
        print("closing", output_filename, start_frame, frames_written) 
        output_file.release()
    else:    
        print("calling write_clip", output_filename, start_frame, frames_written)
        write_clip(fi, frames_written)

for fi in frames_with_motion[:1]:
    write_clip(fi, 0)
 
cv2.destroyAllWindows()

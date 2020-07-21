import glob
import cv2
import sys
import time
import numpy as np

class Config:
    root_dir = "//home/corey/github/opencv_py/test"
    new_size_for_video = (620,640) # 2/3 size
    gauss_blur = 9
    screen_scale_factor = .2
    # 0-255
    red_lightness = 50
    red_saturation = 50
    yellow_lightness = 50
    yellow_saturation = 50
    blue_lightness = 70
    blue_saturation = 70
    red1 = (166,180)
    red2 = (0, 14)
    yellow = (25,32)
    blue = (105, 135)
    #blue = (100, 140)
    kernel = np.ones((5,5),np.uint8)

fourcc = cv2.VideoWriter_fourcc(*'avc1')
font = cv2.FONT_HERSHEY_SIMPLEX    

def process_frame(frame):
   
    small_frame = frame[:,200:500]

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
    #both = cv2.bitwise_or(gray_with_holes, colors_without_gray)
   
    colors_without_gray = cv2.erode(colors_without_gray, Config.kernel)
    colors_without_gray = cv2.dilate(colors_without_gray, Config.kernel)

    return [small_frame, colors_without_gray, gray]

def calc_scores(frames):
    orig = frames[0]
    colors_without_gray = frames[1]
    gray = frames[2]
    
    # is the image getting redder?
    b = np.sum(colors_without_gray[:,:,0], dtype=np.int64)
    g = np.sum(colors_without_gray[:,:,1], dtype=np.int64)
    r = np.sum(colors_without_gray[:,:,2], dtype=np.int64)
    color_ratio = 0
    if b + g > 0:
        color_ratio = r/(b + g)

    #orig_sum = np.sum(orig, dtype=np.int64)
    gray_sum = np.sum(gray, dtype=np.int64)

    b2 = np.sum(orig[:,:,0], dtype=np.int64)
    g2 = np.sum(orig[:,:,1], dtype=np.int64)
    r2 = np.sum(orig[:,:,2], dtype=np.int64)
 
    return [color_ratio, b, g, r, gray_sum, b2, g2, r2]

filenames = []
for filename in  glob.iglob(Config.root_dir + '**/*.mp4', recursive=True):
    filenames.append(filename)
filenames.sort()

# init prev_frame
video_capture = cv2.VideoCapture(filenames[0])
ret, frame = video_capture.read()

frames = process_frame(frame)
first = np.copy(frames[0])
prev_frames = frames
prev_scores = calc_scores(prev_frames)
video_capture.release()

for filename in filenames:
    print(filename)
    video_capture = cv2.VideoCapture(filename)
    cnt = 0
    highest_score = 0
    ret, frame = video_capture.read()
    
    while ret == True:
        cnt += 1
        processed_frames = process_frame(frame)
        orig = processed_frames[0]
        curr_scores = calc_scores(processed_frames)
        
        diffs = []
        pcts = []

        text_on_image = str(cnt)
        cv2.putText(orig, text_on_image,
            (10, len(orig) - 20  ), font, 
        .8, (255,255,0), 2, cv2.LINE_AA)

        cv2.imshow("colors", np.hstack([orig, first]))
        cv2.waitKey(100)

        for i in range(0, 5):
            diff = abs(curr_scores[i] - prev_scores[i])
            diffs.append(diff)
            pct = 0
            if prev_scores[i] > 0:
                pct = diffs[i] / prev_scores[i] * 100
            
            pct = int(round(pct))
            pcts.append(pct)
            
        #cv2.imshow("f", frame) 
        #text_on_image = str(motion_percent) + "," + str(cnt)
        #cv2.putText(processed_frame, text_on_image,
        #    (10, len(processed_frame) - 20  ), font, 
        #.8, (255,255,0), 2, cv2.LINE_AA)

        if True or cnt > 50 and cnt < 60:
            print(cnt, pcts[0], pcts[1], pcts[2], pcts[3], pcts[4], curr_scores)
 
            diff_frame = cv2.absdiff(processed_frames[1], prev_frames[1])
            text_on_image = str(cnt)
            #cv2.putText(orig, text_on_image,
            #    (10, len(orig) - 20  ), font, 
            #    .8, (255,255,255), 2, cv2.LINE_AA)

            #cv2.imshow(diff, orig)
            #cv2.waitKey(0)

            #cv2.imshow("orig", orig)    
            #cv2.waitKey(0)     

        if False and cnt == 54:
            diff_frame = cv2.absdiff(processed_frames[0], prev_frames[0])
            #cv2.imshow("diff", diff_frame)
            a = np.copy(processed_frames[0])
            b = np.copy(prev_frames[0])
            a[:,:,1] = 0
            a[:,:,2] = 0
            b[:,:,1] = 0
            b[:,:,2] = 0
            #diff_frame = cv2.absdiff(a,b)
            #cv2.imshow("53-54", np.hstack([processed_frames[0][:,:,0], prev_frames[0][:,:,0]]))
            #cv2.imshow("54", np.hstack([a,b]))
            #cv2.imshow("d", diff_frame)
            cv2.waitKey()

        prev_scores = curr_scores
        prev_frames = processed_frames
        ret, frame = video_capture.read()

        if cnt > 60:
            print("BREAKING AT 60")
            break

    print("highest score", highest_score)
    video_capture.release()
    break

cv2.destroyAllWindows()

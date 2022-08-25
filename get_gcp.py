import cv2
import os
import glob
import sys
import pandas as pd
import matplotlib.pyplot as plt

# tool for creating gcp files

def show_image(filename, window_name, window_size, corner_x, corner_y, image_scale):
    img = cv2.imread(filename)
    img_h, img_w, _ = img.shape
    img_scaled = cv2.resize(img, (round(img_w*image_scale), round(img_h*image_scale)))
    img_h, img_w, _ = img_scaled.shape
    h = window_size[0]
    w = window_size[1]
    y = img_h - h if corner_y + h > img_h else corner_y
    x = img_w - w if corner_x + w > img_w else corner_x
    if y < 0:
        h = img_h
        y = 0
    if x < 0:
        w = img_w
        x = 0
    cv2.resizeWindow(window_name, w, h)
    crop_img = img_scaled[y:y+h, x:x+w]
    cv2.imshow(window_name, crop_img)
    return x, y

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN and not params[0]:
        params[0] = True
        image_scale = params[4]
        params[1] += "{} {} ".format(round((params[2]+x)/image_scale), round((params[3]+y)/image_scale))

def main():
    a = sys.argv
    path = a[1] if len(a) > 1 else "./"
    path_waypoints = "./waypoints.csv"

    if not os.path.exists(path):
        print(f'invalid path: {path}')
        return

    if not os.path.exists(path_waypoints):
        print(f'{path_waypoints} missing')
        return

    filenames = glob.glob(f'{path}/*/*.JPG')
    n = len(filenames)
    if n == 0:
        print(f'no JPG images found at {path}')
        return
    filenames.sort()

    window_name = "GCP Tool"
    result_path = "./gcp.txt"
    waypoints = pd.read_csv(path_waypoints, index_col="label")
    print(waypoints)
    scale_keys = [ord(str(x)) for x in range(10)]

    #[<updated>, <result string>, <corner x>, <corner y>, <image scale>]
    params = [False, "WGS84 UTM 32N", 0, 0, 1]
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, click_event, params)

    window_size=[600, 800]
    step_size = int(0.9*min(window_size))
    new_entry_prepared = False
    index = 0
    while(index < n):
        filename = filenames[index]
        if not new_entry_prepared:
            wp = filename.split("\\")[-2]
            try:
                data = dict(waypoints.loc[wp])
            except KeyError:
                index += 1
                continue
            params[1] += "\n{} {} {} ".format(data["lat"], data["long"], data["ele_correc"])
            print("({}/{}) Waypoint {}: {}".format(str(index+1), str(n), wp, data["comment"]))
            new_entry_prepared = True
        x_corner, y_corner = show_image(filename, window_name, window_size, params[2], params[3], params[4])
        params[2] = x_corner
        params[3] = y_corner
        if params[0]:
            params[1] += filenames[index].split("\\")[-1]
            print(params[1].split("\n")[-1])
            params[0] = False
            new_entry_prepared = False
            index += 1
        else:
            k = cv2.waitKey(20)
            if k == 27: #Esc
                params[1] += "..."
                break
            elif k == 8 and index > 0 and not params[0]: #Backspace
                print("delete entry " + str(index))
                index -= 1
                params[1] = "\n".join(params[1].split("\n")[:-2])
                new_entry_prepared = False
            elif k == ord('+'):
                window_size = [int(float(v)*1.1) for v in window_size]
            elif k == ord('-'):
                window_size = [int(float(v)*0.9) for v in window_size]
            elif k == ord('w'): #Up
                params[3] -= step_size
                if params[3] < 0:
                    params[3] = 0
            elif k == ord('a'): #Left
                params[2] -= step_size
                if params[2] < 0:
                    params[2] = 0
            elif k == ord('s'): #Down
                params[3] += step_size
            elif k == ord('d'): #Right
                params[2] += step_size
            elif k in scale_keys:
                scale_level = float(scale_keys.index(k)) / 10
                if scale_level == 0: scale_level = 1
                params[4] = scale_level
    cv2.destroyAllWindows()
    print("-"*20 + "\n" + params[1])
    file1 = open(result_path, "w")
    file1.write(params[1])
    file1.close()
    print('saved to ' + result_path)

if __name__ == "__main__":
    main()

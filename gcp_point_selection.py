import cv2
import os
import glob
import sys
import pandas as pd

def show_image(filename, window_name):
    img = cv2.imread(filename)
    cv2.imshow(window_name, img)


def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN and not params[0]:
        params[0] = True
        params[1] += f"{x} {y} "

def main():
    a = sys.argv
    path = a[1] if len(a) > 1 else "./"

    if not os.path.exists(path):
        print('invalid path')
        return

    filenames = glob.glob(path + '/*/*.JPG')
    n = len(filenames)
    if n == 0:
        print("no JPG images found")
        return
    filenames.sort()

    window_name = "GCP" #f"GCP for image {image_name} ({index}/{n})"
    window_size=(700, 1700)
    result_path = "./gcp_file.txt"
    waypoints = pd.read_csv("./waypoints.csv", index_col="label")
    print(waypoints)
    
    params = [False, "WGS84 UTM 32N"]
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, window_size[1], window_size[0])
    cv2.setMouseCallback(window_name, click_event, params)

    new_entry_prepared = False
    index = 0
    while(index < n):
        filename = filenames[index]
        if not new_entry_prepared:
            wp = filename.split("\\")[-2]
            data = dict(waypoints.loc[wp])
            params[1] += "\n{} {} {} ".format(data["lat"], data["long"], data["ele_correc"])
            print("({}/{}) Waypoint {}: {}".format(str(index+1), str(n), wp, data["comment"]))
            new_entry_prepared = True
        show_image(filename, window_name)
        if params[0]:
            params[1] += filenames[index].split("\\")[-1]
            print(params[1].split("\n")[-1])
            params[0] = False
            new_entry_prepared = False
            index += 1
        else:
            k = cv2.waitKey(10)
            if k == 27: #Esc
                params[1] += "..."
                break
            elif k == 8 and index > 0 and not params[0]: #Backspace
                print("delete entry " + str(index))
                index -= 1
                params[1] = "\n".join(params[1].split("\n")[:-2])
                new_entry_prepared = False
    cv2.destroyAllWindows()
    print("-"*20 + "\n" + params[1])
    file1 = open(result_path, "w")
    file1.write(params[1])
    file1.close()
    print('saved to "' + result_path + '"')
    
if __name__ == "__main__":
    main()

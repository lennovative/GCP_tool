import cv2
import os
import glob
import sys

def show_image(filename, window_name):
    img = cv2.imread(filename)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, img)
    cv2.resizeWindow(window_name, 1700, 700)

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN and not params[0]:
        params[0] = True
        params[1] += f"\n{x} {y} "       

def main():
    a = sys.argv
    path = a[1] if len(a) > 1 else "./"

    if not os.path.exists(path):
        print('invalid path')
        return

    filenames = glob.glob(path + '/*.JPG')
    filenames.sort()
    n = len(filenames)
    
    params = [False, ""]
    window_name = "GCP" #f"GCP for image {image_name} ({index}/{n})"
    show_image(filenames[0], window_name)
    cv2.setMouseCallback(window_name, click_event, params)

    index = 0
    while(index < n):
        show_image(filenames[index], window_name)
        if params[0]:
            params[1] += filenames[index].split("/")[-1]
            print("(" + str(index+1) + "/" + str(n) + ") " + params[1].split("\n")[-1])
            params[0] = False
            index += 1
        else:
            k = cv2.waitKey(10)
            if k == 27: #Esc
                break
            elif k == 8 and index > 0: #Backspace
                print("delete point " + str(index))
                index -= 1
                s = params[1]
                params[1] = s[:s.rfind('\n')]

    cv2.destroyAllWindows()
    print(params[1])
    result_path = "./gcp_file.txt"
    file1 = open(result_path, "w")
    file1.write(params[1])
    file1.close()
    print('saved to "' + result_path + '"')
    
if __name__ == "__main__":
    main()

import cv2, os, sys
import numpy as np

mouse_x = -1
mouse_y = -1
leftup_x = -1
leftup_y = -1
leftdown_x = -1
leftdown_y = -1

state = -1

color = (0, 255,0)
thickness = 1

ENTER_KEY = 13
ESC_KEY = 27

# keycode for cv2.waitKeyEx()
LEFT  = 2424832
UP    = 2490368
RIGHT = 2555904
DOWN  = 2621440

font = cv2.FONT_HERSHEY_PLAIN
font_size = 2
font_color = (0, 255, 0)
font_pos = (10, 30)

def mouse_event(event, x, y, flags, param):
    global mouse_x, mouse_y, leftdown_x, leftdown_y, leftup_x, leftup_y, state
    
    mouse_x = x
    mouse_y = y

    if event == cv2.EVENT_LBUTTONUP:
        leftup_x = x
        leftup_y = y
        state = 2

    if state != 2 and event == cv2.EVENT_LBUTTONDOWN:
        leftdown_x = x
        leftdown_y = y
        state = 1

def draw_cross(img, x, y):

    img2 = img.copy()
    height, width = img2.shape[:2]
    img2 = cv2.line(img2, (x, 0), (x, height-1), color, thickness)
    img2 = cv2.line(img2, (0, y), (width-1, y), color, thickness)
    return img2

def draw_rect(img, x0, y0, x1, y1):

    img2 = img.copy()
    img2 = cv2.rectangle(img2, (x0, y0), (x1, y1), color, thickness)
    return img2

def applyGamma(frame, gamma = 1):
    look_up_table = np.zeros((256,1), dtype = 'uint8')
    for i in range(256):
        look_up_table[i][0] = pow(i / 255, 1 / gamma) * 255
    return cv2.LUT(frame, look_up_table)

def usage(progName):
    print('%s corrects gamma, tilt and then crops' % progName)
    print('[usage] python %s <image filename>' % progName)

def main():

    global mouse_x, mouse_y, state

    argv = sys.argv
    argc = len(argv)

    if(argc < 2):
        usage(argv[0])
        quit()
   
    base = os.path.basename(argv[1])
    filename = os.path.splitext(base)[0]
    dst_path = 'corrected_%s.png' % filename
    
    while os.path.exists(dst_path):
        dst_path = '_' + dst_path
    
    prev_mouse_x = -1
    prev_mouse_y = -1
    prev_state = -1
    x0 = -1
    y0 = -1
    x1 = -1
    y1 = -1    

    SCALE = 1.0
    prevSCALE = -1.0

    ANGLE = 3600.0
    prevANGLE = -1.0

    GAMMA = 1.0
    prevGAMMA = -1.0

    rot90 = -1
    prevRot90 = -1

    src = cv2.imread(argv[1])
    H, W = src.shape[:2]
    center = (W // 2, H // 2)

    clone1 = src.copy()
    clone2 = src.copy()
    clone3 = src.copy()
    clone4 = src.copy()

    cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback('image', mouse_event)

    print('Hit 1/2/3/4 key to rotate CW/CCW/180/0')
    print('Hit +/- to scale up/down')
    print('Hit G/g to gamma up/down')
    print('Hit arrow-key to rotate 0.1/0.3 degree')
    print('press L-button, drag and release L-button to serect crop area')
    print('Hit Enter-key to execute crop')
    print('Hit s-key to save whole image (uncropped image)')
    print('Hit other-key to re-select crop area')
    print('hit ESC-key to terminate')

    fUPDATE = False

    while True:

        if state != 2 and (mouse_x != prev_mouse_x or 
                mouse_y != prev_mouse_y or 
                GAMMA != prevGAMMA or
                rot90 != prevRot90 or
                SCALE != prevSCALE or 
                ANGLE != prevANGLE):

            if rot90 != prevRot90:
                
                if (rot90 == cv2.ROTATE_90_CLOCKWISE or 
                    rot90 == cv2.ROTATE_90_COUNTERCLOCKWISE or
                    rot90 == cv2.ROTATE_180):

                    clone1 = cv2.rotate(src, rot90)

                else:
                    clone1 = src.copy()
                    
                H, W = clone1.shape[:2]
                center = (W // 2, H // 2)
                fUPDATE = True

            if fUPDATE or GAMMA != prevGAMMA:
            
                if GAMMA != 1.0:
                    clone2 = applyGamma(clone1, GAMMA)
                else:
                    clone2 = clone1.copy()

                fUPDATE = True

            if fUPDATE or ANGLE != prevANGLE:

                if ANGLE % 3600 != 0:

                    #アフィン変換行列を作成する
                    rotate_matrix = cv2.getRotationMatrix2D(center=center, 
                        angle=(ANGLE - 3600)/10, scale=1)

                    clone3 = cv2.warpAffine(src=clone2, M=rotate_matrix, dsize=(W, H))

                else:
                    clone3 = clone2.copy()

                fUPDATE = True

            if fUPDATE or SCALE != prevSCALE:

                if SCALE != 1.0:
                    clone4 = cv2.resize(clone3, (int(W * SCALE), int(H * SCALE)))
                else:
                    clone4 = clone3.copy()

            if state == 1 and leftdown_x != -1 and leftdown_y != -1:
                x0 = leftdown_x
                y0 = leftdown_y
                clone = draw_rect(clone4, x0, y0, mouse_x, mouse_y)

            else: 
                clone = draw_cross(clone4, mouse_x, mouse_y)    
            
            cv2.putText(clone, 'gamma: %.1f' % GAMMA, 
                font_pos, font, font_size, font_color, 2)
            
            prevGAMMA = GAMMA
            prevRot90 = rot90
            prevANGLE = ANGLE
            prevSCALE = SCALE
            prev_mouse_x = mouse_x
            prev_mouse_y = mouse_y
            prevSCALE = SCALE
            cv2.imshow('image', clone)
            fUPDATE = False

        key = cv2.waitKeyEx(10)
    
        if key == ESC_KEY or key == ENTER_KEY or key == ord('s') or key == ord('S'):
            break

        elif key == LEFT:
            ANGLE += 1
        
        elif key == UP:
            ANGLE += 10

        elif key == RIGHT:
            ANGLE -= 1

        elif key == DOWN:
            ANGLE -= 10

        elif key == ord('-'):
            SCALE *= 0.9

        elif key == ord('+'):
            SCALE *= 1.1

        elif key == ord('G'):
            GAMMA += 0.1
    
        elif key == ord('g'):
            GAMMA -= 0.1

        elif key == ord('1'):
            rot90 = cv2.ROTATE_90_CLOCKWISE

        elif key == ord('2'):
            rot90 = cv2.ROTATE_90_COUNTERCLOCKWISE

        elif key == ord('3'):
            rot90 = cv2.ROTATE_180

        elif key == ord('4'):
            rot90 = -1

        elif key != -1:
            state = 0

        if GAMMA < 0.1:
            GAMMA = 0.1

        if GAMMA > 100:
            GAMMA = 100

    if key == ENTER_KEY:
        
        xmin = np.min((leftdown_x, leftup_x, W))
        xmax = np.max((leftdown_x, leftup_x, 0))
        ymin = np.min((leftdown_y, leftup_y, H))
        ymax = np.max((leftdown_y, leftup_y, 0))
        
        left   = int(xmin / SCALE)
        right  = int(xmax / SCALE)
        top    = int(ymin / SCALE)
        bottom = int(ymax / SCALE)

        dst = clone3[top:bottom, left:right]
      
        cv2.imwrite(dst_path, dst)
        print('save %s' % dst_path)

    elif key == ord('s') or key == ord('S'):
       
        cv2.imwrite(dst_path, clone3)
        print('save %s' % dst_path)

    cv2.destroyAllWindows()

if __name__ == '__main__':

    main()

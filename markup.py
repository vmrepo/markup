
import cv2
import numpy as np
import os
from PIL import ImageGrab
import shutil
import math

IMGSDIR = './licplatesapmles'
MARKUPFILE = 'licplatesapmles.csv'
STARTFILEIDX = 0
MAXWIDTH = ImageGrab.grab().size[0] * 0.9
MAXHEIGHT = ImageGrab.grab().size[1] * 0.9

def readmarkup(filename):
    markuppoints = {}
    with open(filename) as f:
        for l in f.read().splitlines():
            l = l.split(',')
            fl, xyss = l[0], [xys.split(' ') for xys in l[1].split('|')]
            ptss = []
            for xys in xyss:
                pts = []
                for i in range(0, len(xys), 2):
                    pts.append((int(xys[i]), int(xys[i + 1])))
                ptss.append(pts)
            markuppoints[fl] = ptss
    return markuppoints

def savemarkup(filename, markuppoints):
    with open(filename, 'w') as f:
        fls = sorted(markuppoints.keys())
        for fl in fls: 
            ptss = markuppoints[fl]
            f.write(fl + ',' + '|'.join([' '.join([str(d) for pt in pts for d in pt]) for pts in ptss]) + '\n')

def imrotate(filename):
    cv2.imwrite(filename, cv2.rotate(cv2.imread(filename), cv2.ROTATE_90_CLOCKWISE))

def onMouse(event, x, y, flags, param):
    global scale
    global pts
    global pts_idx

    if event == cv2.EVENT_LBUTTONDOWN and pts_idx == -1:
        for i in range(len(pts)):
            x_, y_ = pts[i][0] * scale, pts[i][1] * scale
            if math.sqrt((x_ - x) ** 2 + (y_ - y) ** 2) <= 3:
                pts_idx = i
                pts[pts_idx] = int(x / scale), int(y / scale)
                break
        if pts_idx == -1:    
            pts.append((int(x / scale), int(y / scale)))

    if event == cv2.EVENT_LBUTTONUP and pts_idx != -1:
        pts[pts_idx] = int(x / scale), int(y / scale)
        pts_idx = -1

    if event == cv2.EVENT_MOUSEMOVE and pts_idx != -1:
        pts[pts_idx] = int(x / scale), int(y / scale)

def markup(idx, filename, ptss_ = None):
    global scale
    global pts
    global pts_idx

    winname = '[' + str(idx) + ']' + filename

    img = cv2.imread(filename)
    h, w = img.shape[:2]

    if w > MAXWIDTH and h > MAXHEIGHT:

       scale = MAXWIDTH / w
       if scale * h > MAXHEIGHT:
           scale = MAXHEIGHT / h

    elif w > MAXWIDTH:

       scale = MAXWIDTH / w

    elif h > MAXHEIGHT:

       scale = MAXHEIGHT / h

    elif w > h:

       scale = MAXWIDTH / w
       if scale * h > MAXHEIGHT:
           scale = MAXHEIGHT / h
    else:

       scale = MAXHEIGHT / h
       if scale * w > MAXWIDTH:
           scale = MAXWIDTH / w

    if scale != 1.0:
        img = cv2.resize(img, (int(scale * w), int(scale * h)))

    ptss = [] if ptss_ is None else [[pt for pt in pts] for pts in ptss_]

    current = 0
    if len(ptss) == 0:
        ptss.append([])

    pts_idx = -1

    while True:

        img_ = img.copy()

        for idx, pts in enumerate(ptss):

            clr = (0,0,255) if idx == current else (255,0,0)

            if len(pts) > 1:

                for i in range(len(pts) - 1):
                    pt0 = int(pts[i][0] * scale), int(pts[i][1] * scale)
                    pt1 = int(pts[i + 1][0] * scale), int(pts[i + 1][1] * scale)
                    cv2.circle(img_, pt0, 3, clr, -1)
                    cv2.circle(img_, pt1, 3, clr, -1)
                    cv2.line(img_, pt0, pt1, clr, 1)

                if len(pts) > 3:
                    pt0 = int(pts[0][0] * scale), int(pts[0][1] * scale)
                    pt1 = int(pts[len(pts) - 1][0] * scale), int(pts[len(pts) - 1][1] * scale)
                    cv2.line(img_, pt0, pt1, clr, 1)

            elif len(pts) == 1:
                pt = int(pts[0][0] * scale), int(pts[0][1] * scale)
                cv2.circle(img_, pt, 3, clr, -1)

        pts = ptss[current]

        cv2.imshow(winname, img_)
        cv2.moveWindow(winname, 10, 10)
        cv2.setMouseCallback(winname, onMouse)

        ch = cv2.waitKey(50)

        #exit without saving
        if ch == 27:#Esc
            ptss = []
            break

        #save and move to next image
        if ch == 13:#Enter
            if len(pts) > 3 or (len(ptss) > 1 and len(pts) == 0):
                if len(pts) == 0:
                    del ptss[current]
                else:
                    ptss[current] = pts
                break
            if len(pts) == 0:
                break

        #move to previous image without saving
        if ch == 47:#/
            ptss = -1
            break

        #remove markup
        if ch == 42:#*
            ptss = False
            break

        #moving from region to region
        if ch == 9:#Tab
            if (len(pts) > 3 and len(ptss) > 1) or (len(ptss) > 1 and len(pts) == 0):
                if len(pts) == 0:
                    del ptss[current]
                else:
                    ptss[current] = pts
                current = current + 1 if current + 1 < len(ptss) else 0

        #begin new region
        if ch == 43:#+
            if len(pts) > 3:
                ptss[current] = pts
                ptss.append([])
                current = len(ptss) - 1

        #delete the last entered point of the current region
        if ch == 8:#Backspace
            if len(pts) != 0:
                pts.pop()

        #remove markup and rotation 90 degrees
        if ch == 114:#r
            ptss = -2
            break

    cv2.destroyWindow(winname)

    return ptss


def main():

    isbackup = False

    markuppoints = readmarkup(MARKUPFILE) if os.path.exists(MARKUPFILE) else {}

    files = os.listdir(IMGSDIR)

    startidx = STARTFILEIDX
    idx = 0

    while idx < len(files):

        fl = files[idx]

        if startidx < 0:
            if fl in markuppoints.keys():
                idx += 1
                continue
        elif idx < startidx:
            idx += 1
            continue

        filename = os.path.join(IMGSDIR, fl)

        if not fl in markuppoints.keys():
            ptss = markup(idx,filename)
        else:
            ptss_ = markuppoints[fl]
            ptss = markup(idx,filename, ptss_)

        if ptss == -1:
            startidx = 0
            idx = (idx - 1) if idx > 0 else 0
            continue

        elif ptss == -2:
            imrotate(filename)
            if fl in markuppoints.keys():
                markuppoints.pop(fl)
            idx -= 1

        elif ptss == False:
            if fl in markuppoints.keys():
                markuppoints.pop(fl)
            else:
                idx += 1
                continue

        elif len(ptss) == 0:
            print('Userbreak')
            exit()

        elif len(ptss[0]) == 0:
            idx += 1
            continue

        elif fl in markuppoints.keys() and ptss == ptss_:
            idx += 1
            continue

        else:
            markuppoints[fl] = ptss

        if not isbackup and os.path.exists(MARKUPFILE):
            shutil.copyfile(MARKUPFILE, MARKUPFILE + '.bak')
        isbackup = True

        savemarkup(MARKUPFILE, markuppoints)

        idx += 1

    print('All files')

if __name__ == '__main__':
    main()

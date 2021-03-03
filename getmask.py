
import cv2
import numpy as np
import os

IMGSDIR = './images'
MARKUPFILE = 'markup.csv'
DESTDIR = './masked'

def getmask(ptss, size):
    w, h = size
    mask = np.zeros((h, w), np.uint8)
    for pts in ptss:
        cv2.fillPoly(mask, [np.array(pts)], 1)
    return mask

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

def main():

    markuppoints = readmarkup(MARKUPFILE)

    for filename in sorted(markuppoints.keys()):
        print(filename)
        img = cv2.imread(os.path.join(IMGSDIR, filename))
        h, w = img.shape[:2]
        ptss = markuppoints[filename]
        mask = getmask(ptss, (w, h))
        cv2.imwrite(os.path.join(DESTDIR, filename), mask * 255)

if __name__ == '__main__':
    main()

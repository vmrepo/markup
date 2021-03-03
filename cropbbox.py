
import cv2
import numpy as np
import os

IMGSDIR = './images'
MARKUPFILE = 'markup.csv'
DESTDIR = './cropped'

def getrect(pts, scale, size):
    w, h = size
    xmin, ymin = w, h
    xmax, ymax = 0, 0
    for pt in pts:
        xmin = min(xmin, pt[0])
        ymin = min(ymin, pt[1])
        xmax = max(xmax, pt[0])
        ymax = max(ymax, pt[1])
    rc = (xmin, ymin, xmax - xmin, ymax - ymin)
    rc = (int(rc[0] + rc[2] / 2 * (1 - scale)), int(rc[1] + rc[3] / 2 * (1 - scale)), int(rc[2] * scale), int(rc[3] * scale))
    rc = (0 if rc[0] < 0 else rc[0], 0 if rc[1] < 0 else rc[1], w - rc[0] if (rc[0] + rc[2]) > w else rc[2], h - rc[1] if (rc[1] + rc[3]) > h else rc[3])
    return rc

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
        pts = markuppoints[filename][0]
        rc = getrect(pts, 1.0, (w, h))
        cv2.imwrite(os.path.join(DESTDIR, filename), img[rc[1] : rc[1] + rc[3], rc[0] : rc[0] + rc[2]])

if __name__ == '__main__':
    main()

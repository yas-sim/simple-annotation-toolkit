import os
import sys
import re

import cv2
import argparse

def fileNameDecode(fileName):
    base, ext = os.path.splitext(fileName)
    base, w, h, x, y = re.findall(r'(.*)_([0-9]+)x([0-9]+)\+([0-9]+)\-([0-9]+)', base)[0]
    return int(w), int(h), int(x), int(y), base+ext

def fitImage(img, maxW=1920, maxH=1080):
    h,w,_ = img.shape
    if w>maxW:  scaleX = w/maxW
    else:       scaleX = 1.0
    if h>maxH:  scaleY = h/maxH
    else:       scaleY = 1.0
    scale = scaleX if scaleX>scaleY else scaleY            
    if scale != 1.0:
        img = cv2.resize(img, None, fx=1./scale, fy=1./scale)
    return img, scale

def displayPicture(fileName):
    img = cv2.imread(fileName)
    img, scale = fitImage(img, 1920, 1080)
    w,h,x,y,_ = fileNameDecode(fileName)
    cv2.rectangle(img, (int(x/scale), int(y/scale)), (int((x+w-1)/scale), int((y+h-1)/scale)), (0,255,255), 2)
    cv2.putText(img, fileName, (0, 32), cv2.FONT_HERSHEY_PLAIN, 2, (  0,  0,  0), 3)
    cv2.putText(img, fileName, (0, 32), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 1)
    cv2.imshow('Image+ROI', img)
    return cv2.waitKey(0)


def main(args):
    if args.input!=None:
        displayPicture(args.input)
    if args.directory!=None:
        files = os.listdir(args.directory)
        idx=0
        key=-1
        while key!=27:
            key = displayPicture(os.path.join(args.directory,files[idx]))
            if key==ord('q'):
                idx-=1
                if idx<0: idx=0
            else:
                idx+=1
                if idx>=len(files): idx=len(files)-1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='input image file')
    parser.add_argument('-d', '--directory', type=str, help='input image directory')
    args = parser.parse_args()
    if args.input==None and args.directory==None:
        print('Either one of input file or input directory must be specified.', file=sys.stderr)
        sys.exit(-1)
    main(args)

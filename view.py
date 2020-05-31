# -*- coding: utf-8 -*-
import os
import sys
import re
import glob

import numpy as np
import cv2
import argparse

def fileNameDecode(fileName):
    base, ext = os.path.splitext(fileName)
    grep = re.findall(r'(.*)_([0-9]+)x([0-9]+)\+([0-9]+)\-([0-9]+)', base)
    if len(grep)>0:
        base, w, h, x, y = grep[0]
    else:
        base=base
        w=-1
        h=-1
        x=-1
        y=-1
    return int(w), int(h), int(x), int(y), base+ext

def fitImage(img, maxW=1920, maxH=1080):
    maxW *= 0.5
    maxH *= 0.5
    h,w,_ = img.shape
    scaleX = maxW / w
    scaleY = maxH / h
    if scaleX>1 or scaleY>1:    # Shrink
        scale = 1/min(scaleX, scaleY)
    else:                       # Enlarge
        scale = 1/max(scaleX, scaleY)
    if scale != 1.0:
        img = cv2.resize(img, None, fx=1./scale, fy=1./scale, interpolation=cv2.INTER_CUBIC)
    return img, scale

def displayPicture(fileName):
    img = cv2.imread(fileName)
    if img is None:
        img = np.zeros((300,300,3), dtype=np.uint8)  # dummy image
        cv2.putText(img, 'not an image', (0,32), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1)
    img, scale = fitImage(img, 1920, 1080)
    w,h,x,y,_ = fileNameDecode(fileName)
    if w!=-1:
        cv2.rectangle(img, (int(x/scale), int(y/scale)), (int((x+w-1)/scale), int((y+h-1)/scale)), (0,255,255), 2)
    cv2.putText(img, fileName, (0, 32), cv2.FONT_HERSHEY_PLAIN, 2, (  0,  0,  0), 3)
    cv2.putText(img, fileName, (0, 32), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 1)
    cv2.imshow('Image+ROI', img)
    return cv2.waitKey(0)


def keyHelp():
    print('q: previous image')
    print('w: (or any key) next image')
    print('ESC: exit program')


def main(args):
    if args.input!=None:
        print('hit any key to exit')
        displayPicture(args.input)

    if args.directory!=None:
        keyHelp()

        print('Checking image files...', end='', flush=True)
        tmp_files = glob.glob(args.directory+'/**', recursive=True)
        # Check whether image file or not
        files = []
        for file in tmp_files:
            if os.path.isfile(file):
                img=cv2.imread(file)
                if not img is None:
                    files.append(file)
        print('Completed')
        print('{} data found'.format(len(files)))

        idx=0
        key=-1
        while key!=27:
            key = displayPicture(files[idx])
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

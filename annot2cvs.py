
# -*- coding: utf-8 -*-
import os
import sys
import re
import glob

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

def main(args):
    with open(args.output, 'wt', encoding='utf_8') as f:
        files = glob.glob(args.input+'/**', recursive=True)
        for file in files:
            if os.path.isfile(file):
                img = cv2.imread(file)
                ih,iw = img.shape[:2]
                w,h,x,y,fileName = fileNameDecode(file)
                pathes=fileName.split(os.sep)
                if w!=-1:
                    # filename, classID, x0, y0, x1, y1, iamgeW, imageH
                    f.write('{},{},{},{},{},{},{},{}\n'.format(pathes[-1], pathes[-2], x, y, x+w-1, y+h-1,iw,ih))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input annotation data directory')
    parser.add_argument('-o', '--output', type=str, required=True, help='output CSV file name')
    args = parser.parse_args()
    main(args)

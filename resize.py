# -*- coding: utf-8 -*-
import os
import glob

import cv2
import numpy as np
import argparse

def main(args):
    if args.output==None:
        outdir = args.input + '_resized'
    else:
        outdir = args.output

    size = eval(args.size)

    files = glob.glob(args.input+'/**', recursive=True)
    for file in files:
        if os.path.isfile(file):
            img=cv2.imread(file)
            if not img is None:
                pad = np.full((size[0], size[1], 3), eval(args.padding_color), dtype=np.uint8)
                if args.keep_aspect_ratio==False:
                    img = cv2.resize(img, size)
                else:
                    h,w,_ = img.shape
                    if w/size[0] > h/size[1]:
                        rw = size[0]
                        rh = int(h/(w/size[0]))
                        img = cv2.resize(img, (rw, rh), interpolation=cv2.INTER_CUBIC)
                        toppad = (size[1]-rh)//2
                        pad[toppad:toppad+rh, :] = img
                    else:
                        rw = w/(h/size[1])
                        rh = size[1]
                        img = cv2.resize(img, (rw, rh), interpolation=cv2.INTER_CUBIC)
                        sidepad = (size[0]-rw)//2
                        pad[:, sidepad:sidepad+rw] = img
                    img = pad

                fname = os.path.join(outdir, file)
                base, ext = os.path.split(fname)
                print(fname, base, ext)
                os.makedirs(base, exist_ok=True)
                cv2.imwrite(os.path.join(outdir, file), img)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input image directory')
    parser.add_argument('-o', '--output', type=str, required=False, help='output image directory')
    parser.add_argument('-s', '--size', required=True, help='resize image size (w,h)')
    parser.add_argument('--keep_aspect_ratio', action='store_true', required=False, default=False, help='keep original aspect ratio')
    parser.add_argument('--padding_color', type=str, required=False, default="(0,0,0)", help='color for padding (default=(0,0,0), (b,g,r))')
    args = parser.parse_args()

    main(args)

# -*- coding: utf-8 -*-
# # ROI annotation tool
import sys
import os
import shutil
import re

import cv2
import numpy as np 

import argparse

g_colorTbl = [
    (  0,  0,  0), (255,  0,  0), (  0,  0,255), (255,  0,255),
    (  0,255,  0), (255,255,  0), (  0,255,255), (255,255,255) 
]

def dispCursor(img, x, y, scale=1.0, cursorInfoFlag=False):
    h, w = img.shape[:1+1]
    if x>=w: x=w-1
    if y>=h: y=h-1
    color = tuple(img[y,x])
    negCol = (int(255-color[0]), int(255-color[1]), int(255-color[2]))
    cv2.line(img, (0,y), (img.shape[1],y), negCol, 1)
    cv2.line(img, (x,0), (x,img.shape[0]), negCol, 1)
    if cursorInfoFlag==True:
        string = '({},{})-{}'.format(int(x*scale), int(y*scale), color)
        cv2.putText(img, string, (x,y), cv2.FONT_HERSHEY_PLAIN, 1, (  0,  0,  0), 3)
        cv2.putText(img, string, (x,y), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1)
    return img

def dispRectangle(img, p0, p1, color):
    global g_colorTbl
    cv2.rectangle(img, p0, p1, g_colorTbl[color%len(g_colorTbl)], 2)
    return img

def dispROIs(img, rois):
    global g_colorTbl
    for roi in rois:
        if 'roi' in roi:
            x0,y0,x1,y1 = rois[roi]
            _, roiId, clsId = roi.split('_')
            roiId = int(roiId)
            clsId = int(clsId)
            color = clsId % len(g_colorTbl)
            cv2.rectangle(img, (x0,y0), (x1,y1), g_colorTbl[color],2)
            cv2.putText(img, str(clsId), (x0,y0), cv2.FONT_HERSHEY_PLAIN, 1.5, g_colorTbl[color], 2)
    return img

g_mouseX = 0
g_mouseY = 0
g_mouseBtn = 0

def onMouse(event, x, y, flags, param):
    global g_mouseX, g_mouseY
    global g_mouseBtn

    g_mouseX = x
    g_mouseY = y

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

def fileNameEncode(fileName, w, h, x, y):
    base, ext = os.path.splitext(fileName)
    base = '{}_{}x{}+{}-{}'.format(base, int(w), int(h), int(x), int(y))
    return base+ext

def fitImage(img, maxW=1920, maxH=1080):
    h,w,_ = img.shape
    if h>maxH or w>maxW:
        # shrink
        if w>maxW:  scaleX = w/maxW
        else:       scaleX = 1.0
        if h>maxH:  scaleY = h/maxH
        else:       scaleY = 1.0
        scale = scaleX if scaleX>scaleY else scaleY
    else:
        # enlarge
        scaleX = 1./(maxW//w)
        scaleY = 1./(maxH//h)
        scale = scaleX if scaleX>scaleY else scaleY
    if scale != 1.0:
        img = cv2.resize(img, None, fx=1./scale, fy=1./scale, interpolation=cv2.INTER_CUBIC)
    return img, scale



def keyHelp():
    print('q: previous image')
    print('w: next image')
    print('u: undo (remove the last ROI in current image)')
    print('0-9: start / end of ROI (hit numeric key to start drawing ROI and hit numeric key to finish drawing. no need to keep pressing)')
    print('W: (capital) write annotation data to the output directory')
    print('c: toggle cursor info (x, y, color on the cursor)')
    print('ESC: exit program')


def main(args):
    global g_mouseX, g_mouseY

    inputDir = args.input
    files = os.listdir(inputDir)
    annotation = [ { 'fname':file } for file in files if os.path.isfile(os.path.join(inputDir, file))==True]
    if len(annotation)==0:
        print('no file is found in {}'.format(inputDir), file=sys.stderr)
        sys.exit(-1)
    annotIdx = 0
    print(annotation)

    keyHelp()

    cv2.namedWindow('work')
    cv2.setMouseCallback('work', onMouse)

    updateFlag=True
    drawingFlag=False
    cursorInfoFlag=True
    x0=0
    y0=0
    color=0
    scale=1
    maxW=1920
    maxH=1080
    while True:
        if updateFlag==True:
            file = os.path.join(inputDir, annotation[annotIdx]['fname'])
            srcImg = cv2.imread(file)
            if srcImg is None:
                srcImg = np.zeros((300,300,3), dtype=np.uint8)  # dummy image
                cv2.putText(srcImg, 'not an image', (0,32), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1)
            srcImg, scale = fitImage(srcImg, maxW, maxH)
            updateFlag=False

        dispImg = dispCursor(srcImg.copy(), g_mouseX, g_mouseY, scale, cursorInfoFlag)
        if drawingFlag==True:
            dispImg = dispRectangle(dispImg, (x0,y0), (g_mouseX, g_mouseY), color)
        dispImg = dispROIs(dispImg, annotation[annotIdx])
        cv2.imshow('work', dispImg)
        key = cv2.waitKey(100)

        if key==27: break

        if key>=ord('0') and key<=ord('9'):
            if drawingFlag==False:
                drawingFlag=True
                x0 = g_mouseX
                y0 = g_mouseY
                color = key-ord('0')
            else:
                drawingFlag=False
                roiIdx = len(annotation[annotIdx])-1
                clsId = key-ord('0')
                roi = [x0, y0, g_mouseX, g_mouseY]
                annotation[annotIdx]['roi_{}_{}'.format(roiIdx, clsId)] = roi
                print('marked a ROI \'{} {}\''.format(clsId, roi))

        if key==ord('u'):
            delKey = list(annotation[annotIdx].keys())[-1]
            if 'roi' in delKey:
                roi = annotation[annotIdx][delKey]
                del annotation[annotIdx][delKey]
                print('removed \'{} {}\''.format(delKey, roi))
            else:
                print('no ROI to remove')

        if key==ord('q'):
            annotIdx-=1
            if annotIdx<0:
                annotIdx = 0
            updateFlag=True
            print('previous image \'{}\''.format(annotation[annotIdx]['fname']))
        if key==ord('w'):
            annotIdx+=1
            if annotIdx>=len(annotation):
                annotIdx=len(annotation)-1
            updateFlag=True
            print('next image \'{}\''.format(annotation[annotIdx]['fname']))
        
        if key==ord('W'):
            try:
                os.mkdir(args.output)
            except FileExistsError:
                pass
            for annot in annotation:
                fname = annot['fname']
                for roi in annot:
                    if 'roi' in roi:
                        _,_,clsId = roi.split('_')
                        x0,y0,x1,y1 = annot[roi]
                        x0*=scale
                        y0*=scale
                        x1*=scale
                        y1*=scale
                        try:
                            os.mkdir(os.path.join(args.output, str(clsId)))
                        except FileExistsError:
                            pass
                        inPath = os.path.join(args.input, fname)
                        outPath = os.path.join(args.output, str(clsId), fileNameEncode(fname, x1-x0+1, y1-y0+1, x0, y0))
                        shutil.copy(inPath, outPath)
            print('Wrote the current ROI data to the output directory {}'.format(args.output))
        
        if key==ord('c'):
            cursorInfoFlag = True if cursorInfoFlag==False else False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input image directory')
    parser.add_argument('-o', '--output', type=str, required=True, help='data output directory')
    args = parser.parse_args()

    main(args)

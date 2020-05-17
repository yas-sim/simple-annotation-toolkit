# -*- coding: utf-8 -*-
import os
from xml.etree.ElementTree import *

import argparse

def writeXMLRecord(fo, fname, folder, iw, ih, objs):
    fo.write('<folder>{}</folder>\n'.format(folder))
    fo.write('<filename>{}</filename>\n'.format(fname))
    fo.write('<path>{}</path>\n'.format(os.path.join(folder, fname)))
    fo.write('<source><database>{}</database></source>\n'.format('Unknown'))
    fo.write('<size><width>{}</width><height>{}</height><depth>{}</depth>\n'.format(iw, ih, 3))
    fo.write('<segmented>{}</segmented>\n'.format(0))
    for obj in objs:
        clsid, x0, y0, x1, y1 = obj
        fo.write('  <object>\n')
        fo.write('    <name>{}</name><pose>{}</pose><truncated>{}</truncated><difficult>{}</difficult>\n'.format(clsid, 'Unspecified', 0, 0))
        fo.write('    <bndbox><xmin>{}</xmin><ymin>{}</ymin><xmax>{}</xmax><ymax>{}</ymax></bndbox>\n'.format(x0, y0, x1, y1))
        fo.write('  </object>\n')

def main(args):
    with open(args.input, 'rt', encoding='utf_8') as fi:
        lines = fi.readlines()
        annots = {}
        for line in lines:
            fname, clsid, x0, y0, x1, y1, iw, ih= line.split(',')
            obj = [clsid, x0, y0, x1, y1]
            if fname in annots:
                annots[fname]['objects'].append(obj)
            else:
                annots[fname]={'width':iw, 'height':ih, 'objects':[]}
    with open(args.output, 'wt', encoding='utf_8') as fo:
        fo.write('<annotation>\n')
        for annot in annots:
            writeXMLRecord(fo, annot, args.folder, annots[annot]['width'], annots[annot]['height'], annots[annot]['objects'])
        fo.write('</annotation>\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='input csv file name')
    parser.add_argument('-o', '--output', type=str, required=True, help='output pascal voc file name')
    parser.add_argument('--folder', type=str, default='__FOLDER__', required=False, help='folder name')
    args = parser.parse_args()
    main(args)

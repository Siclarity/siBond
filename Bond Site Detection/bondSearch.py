from builtins import print as println
from gdsii.record import Record
from gdsii.tags import type_of_tag, DICT
from gdsii.types import NODATA, ASCII, BITARRAY, REAL8, INT2, INT4
import logging
import json
import os
import klayout.db as pya
from rtree import index
from datetime import datetime
rtree = index.Index()
ly = pya.Layout()
ly.read("11700_TEL_Die2_on_Die1_R2b.gds")

top_cell = ly.top_cell()
layer1 = ly.layer(110, 0)
layer2 = ly.layer(11, 0)
layer3 = ly.layer(4,0) #intersection layer will be added
shapes1 = []
start_time=datetime.now()
for idx, shape in enumerate(top_cell.shapes(layer1).each()):
    # if shape.is_polygon():
    #     print("Polygon: " + str(shape.dpolygon))
    # elif shape.is_path():
    #     print("Path: " + str(shape.dpath))
    # elif shape.is_text():
    #     print("Text: " + str(shape.dtext))
    # elif shape.is_box():
    #     print("Box: " + str(shape.dbox))
    #print(shape)
    bnds = shape.bbox()
    bnd = (bnds.left, bnds.bottom, bnds.right, bnds.top)
    shapes1.append(shape)
    rtree.insert(idx, bnd)
end_time=datetime.now()
print('Duration of Layer 1 enumeration: {}'.format(end_time - start_time))
print('Shape 1 array size:',len(shapes1))

intersecting_site=[]
full_match = 0 
offset_match = 0
shape1_left_set = set()
shape2_left = 0
shapes2=[]
from collections import defaultdict
types_of_contacts = defaultdict(lambda:0)
start_time=datetime.now()
for idx, shape in enumerate(top_cell.shapes(layer2).each()):
    bnds = shape.bbox()
    bnd = (bnds.left, bnds.bottom, bnds.right, bnds.top)
    shapes2.append(shape)
    match = list(rtree.intersection(bnd))
    if len(match):
        for id in match:
            intersecting_site.append([shape,shapes1[id]])
            l1 = pya.Shapes()
            l1.insert(shape)
            lcheck = pya.Region(l1)
            r1 = pya.Shapes()
            r1.insert(shapes1[id])
            rcheck = pya.Region(r1)
            top_cell.shapes(layer3).insert(lcheck &  rcheck)
            if (lcheck^rcheck).is_empty():
                full_match+=1
            else:
                offset_match+=1
            shape1_left_set.add(id)
    else:
        shape2_left +=1
    shape1_left = len(shapes1) - len(shape1_left_set)
end_time=datetime.now()
print('Duration of Layer 2 enumeration: {}'.format(end_time - start_time))
ly.write("MELD_V0_out_modified.gds")
print(f'full_match : {full_match }')
print(f'offset_match : {offset_match }')
print(f'shape1_unmatched : {shape1_left }')
print(f'shape2_unmatched : {shape2_left }')

def classification(a):
    if a.is_polygon():
        a="Polygon"
    elif a.is_path():
        a="Path"
    elif a.is_text():
        a="Text"
    elif a.is_box():
        a="Box"
    else:
        a="unidentified"

    return a

def full_match(a,b):
    c=a
    d=b
    #return(((c.left<=d.left<=c.right) and (c.left <=d.right<=c.right) and (c.bottom<=d.bottom<=c.top)  and (c.bottom<=d.top<=c.top)) or((d.left<=c.left<=d.right) and (d.left <=c.right<=d.right) and (d.bottom<=c.bottom<=d.top)  and (d.bottom<=c.top<=d.top)))
    return ((c.left==d.left) and (c.bottom==d.bottom) and (c.right==d.right) and (c.top==d.top))
start_time=datetime.now()
total_fullmatch=0
total_offsetmatch=0
classify_sites=[]
unique_sites=[]
for i in range(0,len(intersecting_site)):
    a=intersecting_site[i][0].bbox()
    b=intersecting_site[i][1].bbox()
    min_left=min(a.left,b.left)
    max_left=max(a.left,b.left)
    min_bot=min(a.bottom,b.bottom)
    max_bot=max(a.bottom,b.bottom)
    min_right=min(a.right,b.right)
    max_right=max(a.right,b.right)
    min_top=min(a.top,b.top)
    max_top=max(a.top,b.top)
    c=classification(intersecting_site[i][0])
    d=classification(intersecting_site[i][1])
    #effective_area=abs(abs((min_left-max_right)*(m_bot-max_top))-abs((abs(a.right-b.right)-abs(a.left-b.left))*(abs(a.top-b.top)-abs(a.bottom-b.bottom))))
    #effective_area=abs((abs((abs(a.right)-abs(b.right)))-abs((abs(a.left)-abs(b.left))))*abs((abs((abs(a.top)-abs(b.top)))-abs((abs(a.bottom)-abs(b.bottom))))))
    effective_area=abs((abs(min_left)-abs(min_right))*(abs(min_bot)-abs(min_top)))
    #if((min_left==a.left and min_bot==a.bottom and max_right==a.right and max_top==a.top) or (min_left==b.left and min_bot==b.bottom and max_right==b.right and max_top==b.top)):
    if(full_match(a,b)):
        site=["FM",effective_area,c,d]#intersecting_site[i][0],intersecting_site[i][1]]
        alt_site=["FM",effective_area,d,c]
        classify_sites.append([site,a,b])
        total_fullmatch+=1
        if site in unique_sites or alt_site in unique_sites:
            continue
        else:
            unique_sites.append(site)
    else:
        site=["OM",effective_area,c,d]#intersecting_site[i][0],intersecting_site[i][1]] need to get the shape of these to ensure they are not the same
        alt_site=["OM",effective_area,d,c]
        classify_sites.append([site,a,b])
        total_offsetmatch+=1
        if site in unique_sites or alt_site in unique_sites:
            continue
        else:
            unique_sites.append(site)
end_time=datetime.now()

# print(unique_sites)
print("Total number of unique sites:",len(unique_sites))
print("Full Matched:",total_fullmatch)
print("Offset Matched:",total_offsetmatch)
# print(classify_sites[22])
print("Total time:",(end_time-start_time))

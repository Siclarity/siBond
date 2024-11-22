from builtins import print as println
from gdsii.record import Record
from gdsii.tags import type_of_tag, DICT
from gdsii.types import NODATA, ASCII, BITARRAY, REAL8, INT2, INT4
import logging
import json
import os
import klayout.db as pya
from klayout import lay
from rtree import index
from datetime import datetime
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

#filename="CLIP.gds"
filename="Test.gds"
#filename="displacement.gds"
def search(filename):
    if(filename.lower().endswith('.gds')):
        rtree = index.Index()
        ly = pya.Layout()
        ly.read(filename)
        print(f"Layout contains {(ly.layers())} layers.")
        #print(f"Viewer contains {(view.current_layer_list)} layers.")
        top_cell = ly.top_cell()
        top_cell.flatten(-1,True)
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
        shape1_left=0
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
        ly.write("MELD_V0_out.gds")
        print(f'full_match : {full_match }')
        print(f'offset_match : {offset_match }')
        print(f'shape1_unmatched : {shape1_left }')
        print(f'shape2_unmatched : {shape2_left }')

        # for items in intersecting_site:
        #     print(items)
        #Create a map of the intersecting sites
        intersection_map={}
        for pair in intersecting_site:
            a=str(pair[0])
            b=str(pair[1])
            if b in intersection_map:
                intersection_map[b].append(a)
            else:
                intersection_map[b]=[a]
        for key, value in intersection_map.items():
            print(f"{key}: {', '.join(value)}")
        start_time=datetime.now()
        total_fullmatch=0
        total_offsetmatch=0
        classify_sites=[]
        unique_sites=[]
        unique_sites_dict={}
        count=0
        for i in range(0,len(intersecting_site)):
            #print(f"Intersecting site:{i}")
            a=intersecting_site[i][0].bbox()
            b=intersecting_site[i][1].bbox()
            #print(f"A Bounds:{a}")
            #print(f"B Bounds:{b}")
            min_left=min(a.left,b.left)
            #print(f"Min Left:{min_left}")
            max_left=max(a.left,b.left)
            #print(f"Max Left:{max_left}")
            min_bot=min(a.bottom,b.bottom)
            #print(f"Min Bot:{min_bot}")
            max_bot=max(a.bottom,b.bottom)
            #print(f"Max Bot:{max_bot}")
            min_right=min(a.right,b.right)
            #print(f"Min Right:{min_right}")
            max_right=max(a.right,b.right)
            #print(f"Max Right:{max_right}")
            min_top=min(a.top,b.top)
            #print(f"Min Top:{min_top}")
            max_top=max(a.top,b.top)
            #print(f"Max Top:{max_top}")
            c=classification(intersecting_site[i][0])
            d=classification(intersecting_site[i][1])
            width=(min_right-max_left)
            height=(min_top-max_bot)
            effective_area=abs(width*height)
            #effective_area=abs(abs((min_left-max_right)*(min_bot-max_top))-abs((abs(a.right-b.right)-abs(a.left-b.left))*(abs(a.top-b.top)-abs(a.bottom-b.bottom))))
            #print(f"(({min_left}-{max_right})*({min_bot}-{max_top}))-((({a.right}-{b.right})-({a.left}-{b.left}))*(({a.top}-{b.top})-({a.bottom}-{b.bottom})))")
            #effective_area=abs((abs((abs(a.right)-abs(b.right)))-abs((abs(a.left)-abs(b.left))))*abs((abs((abs(a.top)-abs(b.top)))-abs((abs(a.bottom)-abs(b.bottom))))))
            #effective_area=abs((abs(max_left)-abs(min_right))*(abs(max_bot)-abs(min_top)))
            #if((min_left==a.left and min_bot==a.bottom and max_right==a.right and max_top==a.top) or (min_left==b.left and min_bot==b.bottom and max_right==b.right and max_top==b.top)):
            # print(f"{effective_area}, {i}")
            #These variables below are introduced for positioning of the objects and will help with the uniqueness
            x_left=a.left-b.left
            x_right=a.right-b.right
            y_bot=a.bottom-b.bottom
            y_top=a.top-b.top
            x=(x_left+x_right)/2
            y=(y_bot+y_top)/2
            if(a==b):
                site=["FM",effective_area,c,d,x_left,x_right,y_bot,y_top]#intersecting_site[i][0],intersecting_site[i][1]]
                alt_site=["FM",effective_area,d,c,x_left,x_right,y_bot,y_top]
                classify_sites.append([site,a,b])
                total_fullmatch+=1
                if site in unique_sites or alt_site in unique_sites:
                    place=0
                    for items in unique_sites:
                        if site==items:
                            break
                        else:
                            place+=1
                    unique_sites_dict[place]['Similar Sites']+=1

                else:
                    unique_sites.append(site)
                    unique_sites_dict[count]={"Type Match":"Full Match","Shape 1 type:":c,"Shape 1 bounds:":a,"Shape 2 type":d,"Shape 2 bounds:":b, "Area of Intersection:":effective_area, 'Similar Sites':0}
                    count+=1
                    
            else:
                site=["OM",effective_area,c,d,x_left,x_right,y_bot,y_top]#intersecting_site[i][0],intersecting_site[i][1]] need to get the shape of these to ensure they are not the same
                alt_site=["OM",effective_area,d,c,x_left,x_right,y_bot,y_top]
                classify_sites.append([site,a,b])
                total_offsetmatch+=1
                if site in unique_sites or alt_site in unique_sites:
                    place=0
                    for items in unique_sites:
                        if site==items:
                            break
                        else:
                            place+=1
                    unique_sites_dict[place]['Similar Sites']+=1
                else:
                    unique_sites.append(site)
                    unique_sites_dict[count]={"Type Match:":"Offset Match","Shape 1 type:":c,"Shape 1 bounds:":a,"Shape 2 type":d,"Shape 2 bounds:":b, "Area of Intersection:":effective_area, 'Similar Sites':0}
                    count+=1
        end_time=datetime.now()

        # print(unique_sites)
        print("Total number of unique sites:",len(unique_sites))
        print("Full Matched:",total_fullmatch)
        print("Offset Matched:",total_offsetmatch)
        # print(classify_sites[22])
        print("Total time:",(end_time-start_time))
        #print(unique_sites_dict)
        #print(unique_sites_dict[2])
        for key ,value in unique_sites_dict.items():
            print(f"{key}:{value}")
        str_dict = {key: str(value) for key, value in unique_sites_dict.items()}
        return({"success":"Completed the Bond Search Algorithm","Full_Matched":total_fullmatch,"Offset_Matched":total_offsetmatch, "Total_Number_of_Unique_Sites":len(unique_sites), "List_of_unique_bonding_site":str_dict})
    else:
        print(filename)
        return ({"error": "File must be a GDS (.gds) to run site classification"}), 400

#Comment this out when using for application
#search(filename)
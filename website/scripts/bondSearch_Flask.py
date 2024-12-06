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
def calculate_areas(shape1,shape2,shape1_type,shape2_type):
    if shape1_type=="Polygon" and shape2_type=="Box":
        print(f"Shape1{shape1} is a polygon")
        print(f"Shape2 Bounds:{shape2} is a {shape2_type}")
        shape1_left=shape2.left-1000
        shape1_bottom=shape2.bottom-1000
        shape1_right=shape2.right+1000
        shape1_top=shape2.top+1000
        left=max(shape1.left,shape1_left)
        bottom=max(shape1.bottom,shape1_bottom)
        right=min(shape1.right, shape1_right)
        top=min(shape1.top, shape1_top)
        new_poly = pya.DPolygon([pya.DPoint(left, bottom), pya.DPoint(right, bottom), pya.DPoint(right, top), pya.DPoint(left, top)])
        print(f"New Polygon bounds:{new_poly}")
        new_area=new_poly.area()
        print(f"Polygon area:{new_area}")
        box_area=shape1.area()
        print(f"Box area is {box_area}")
        return new_poly,new_area,box_area
    elif shape2_type=="Polygon" and shape1_type=="Box":
        print(f"Shape2{shape2} is a polygon")
        print(f"Shape1 Bounds:{shape1} is a {shape1_type}")
        shape2_left=shape1.left-1000
        shape2_bottom=shape1.bottom-1000
        shape2_right=shape1.right+1000
        shape2_top=shape1.top+1000
        left=max(shape2.left,shape2_left)
        bottom=max(shape2.bottom,shape2_bottom)
        right=min(shape2.right, shape2_right)
        top=min(shape2.top, shape2_top)
        new_poly = pya.DPolygon([pya.DPoint(left, bottom), pya.DPoint(right, bottom), pya.DPoint(right, top), pya.DPoint(left, top)])
        print(f"New Polygon bounds:{new_poly}")
        new_area=new_poly.area()
        print(f"Polygon bounds:{new_area}")
        box_area=shape1.area()
        print(f"Box area is {box_area}")
        return new_poly,new_area,box_area
        
    elif shape1_type=='Polygon' and shape2_type=='Polygon':
        print(f"Shape1{shape1} is a polygon")
        print(f"Shape2{shape2} is a polygon")
        region1=pya.Region(shape1)
        region2=pya.Region(shape2)
        intersection=(region1 & region2)
        intersection_area=intersection.area()
        union=(region1|region2)
        union_area=union.area()
        print(f"Intersection area of the polygons:{intersection_area}")
        print(f"Union area of the polygons:{union_area}")
        return intersection, intersection_area,union,union_area
    else:
        print(f"Shape 1 and 2 are {shape1_type}")
        area1=shape1.area()
        area2=shape2.area()
        print(f"Shape 1 area:{area1}")
        print(f"Shape 2 area:{area2}")
        return area1,area2

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
        sites_visited1=[]
        sites_visited2=[]
        for i in range(0,len(intersecting_site)):
            #print(f"Intersecting site:{i}")
            a=intersecting_site[i][0].bbox()
            b=intersecting_site[i][1].bbox()
            #print(f"A Bounds:{a}")
            # #print(f"B Bounds:{b}")
            # min_left=min(a.left,b.left)
            # #print(f"Min Left:{min_left}")
            # max_left=max(a.left,b.left)
            # #print(f"Max Left:{max_left}")
            # min_bot=min(a.bottom,b.bottom)
            # #print(f"Min Bot:{min_bot}")
            # max_bot=max(a.bottom,b.bottom)
            # #print(f"Max Bot:{max_bot}")
            # min_right=min(a.right,b.right)
            # #print(f"Min Right:{min_right}")
            # max_right=max(a.right,b.right)
            # #print(f"Max Right:{max_right}")
            # min_top=min(a.top,b.top)
            # #print(f"Min Top:{min_top}")
            # max_top=max(a.top,b.top)
            # #print(f"Max Top:{max_top}")
            # c=classification(intersecting_site[i][0])
            # d=classification(intersecting_site[i][1])
            # width=(min_right-max_left)
            # height=(min_top-max_bot)
            # effective_area=abs(width*height)
            #effective_area=abs(abs((min_left-max_right)*(min_bot-max_top))-abs((abs(a.right-b.right)-abs(a.left-b.left))*(abs(a.top-b.top)-abs(a.bottom-b.bottom))))
            #print(f"(({min_left}-{max_right})*({min_bot}-{max_top}))-((({a.right}-{b.right})-({a.left}-{b.left}))*(({a.top}-{b.top})-({a.bottom}-{b.bottom})))")
            #effective_area=abs((abs((abs(a.right)-abs(b.right)))-abs((abs(a.left)-abs(b.left))))*abs((abs((abs(a.top)-abs(b.top)))-abs((abs(a.bottom)-abs(b.bottom))))))
            #effective_area=abs((abs(max_left)-abs(min_right))*(abs(max_bot)-abs(min_top)))
            #if((min_left==a.left and min_bot==a.bottom and max_right==a.right and max_top==a.top) or (min_left==b.left and min_bot==b.bottom and max_right==b.right and max_top==b.top)):
            # print(f"{effective_area}, {i}")
            #These variables below are introduced for positioning of the objects and will help with the uniqueness
            if(a==b):
                # #print(f"A Bounds:{a}")
                # #print(f"B Bounds:{b}")
                # min_left=min(a.left,b.left)
                # #print(f"Min Left:{min_left}")
                # max_left=max(a.left,b.left)
                # #print(f"Max Left:{max_left}")
                # min_bot=min(a.bottom,b.bottom)
                # #print(f"Min Bot:{min_bot}")
                # max_bot=max(a.bottom,b.bottom)
                # #print(f"Max Bot:{max_bot}")
                # min_right=min(a.right,b.right)
                # #print(f"Min Right:{min_right}")
                # max_right=max(a.right,b.right)
                # #print(f"Max Right:{max_right}")
                # min_top=min(a.top,b.top)
                # #print(f"Min Top:{min_top}")
                # max_top=max(a.top,b.top)
                #print(f"Max Top:{max_top}")
                c=classification(intersecting_site[i][0])
                d=classification(intersecting_site[i][1])
                a_area=0
                b_area=0
                if c=="Polygon" and d=="Box":
                    a,a_area=calculate_areas(a,b,c,d)
                    a=a.bbox()
                    print(f"Shape 1's new bbox:{a}")
                    effective_area=min(a_area,b_area)
                    print(f"Effective area:{effective_area}")
                    ineffective_area=max(a_area,b_area)-effective_area
                    print(f"Ineffective area:{ineffective_area}")
                elif c=='Box' and d=='Polygon':
                    b,b_area=calculate_areas(a,b,c,d)
                    b=b.bbox()
                    print(f"Shape 2's new bbox:{b}")
                    effective_area=min(a_area,b_area)
                    print(f"Effective area:{effective_area}")
                    ineffective_area=max(a_area,b_area)-effective_area
                    print(f"Ineffective area:{ineffective_area}")
                elif c=="Polygon" and d=='Polygon':
                    a,a_area,b,b_area=calculate_areas(a,b,c,d)
                    #A will be the intersection area
                    a=a.bbox()
                    #B will be the union area
                    b=b.bbox()
                    effective_area=min(a_area,b_area)
                    print(f"Effective area:{effective_area}")
                    ineffective_area=max(a_area,b_area)-effective_area
                    print(f"Ineffective area:{ineffective_area}")
                else:
                    a_area,b_area=calculate_areas(a,b,c,d)
                    min_left=min(a.left,b.left)
                    max_left=max(a.left,b.left)
                    min_bot=min(a.bottom,b.bottom)
                    max_bot=max(a.bottom,b.bottom)
                    min_right=min(a.right,b.right)
                    max_right=max(a.right,b.right)
                    min_top=min(a.top,b.top)
                    max_top=max(a.top,b.top)
                    effective_width=(min_right-max_left)
                    effective_height=(min_top-max_bot)
                    effective_area=effective_width*effective_height
                    ineffective_width=(max_right-min_left)
                    ineffective_height=(max_top-min_bot)
                    ineffective_area=(ineffective_width*ineffective_height)-effective_area

                print("Passed the reassignment of bounding box/area calculations for the box")
                # width=(min_right-max_left)
                # height=(min_top-max_bot)
                x_left=a.left-b.left
                x_right=a.right-b.right
                y_bot=a.bottom-b.bottom
                y_top=a.top-b.top
                ineffective_area=max(a_area,b_area)-effective_area
                print(f"Ineffective area:{ineffective_area}")
                x=(x_left+x_right)/2
                y=(y_bot+y_top)/2
                site=["FM",effective_area,c,d,x_left,x_right,y_bot,y_top,ineffective_area]#intersecting_site[i][0],intersecting_site[i][1]]
                classify_sites.append([site,a,b])
                total_fullmatch+=1
                if site in unique_sites:
                    print(f"Have seen this full match site:{site} before")
                    # print(f"Position:{x_left,y_bot,x_right,y_top}")
                    place=0
                    for items in unique_sites:
                        if site==items:
                            break
                        else:
                            place+=1
                    unique_sites_dict[place]['Similar Sites']+=1
                    print(f"Here is the site we incremented{unique_sites_dict[place]}")
                else:
                    unique_sites.append(site)
                    unique_sites_dict[count]={"Type Match":"Full Match","Shape 1 type:":c,"Shape 1 bounds:":a,"Shape 2 type":d,"Shape 2 bounds:":b, "Area of Intersection:":effective_area, 'Similar Sites':0}
                    sites_visited1.append(a)
                    sites_visited2.append(b)
                    count+=1
                    
            else:
                # #print(f"A Bounds:{a}")
                # #print(f"B Bounds:{b}")
                # min_left=min(a.left,b.left)
                # #print(f"Min Left:{min_left}")
                # max_left=max(a.left,b.left)
                # #print(f"Max Left:{max_left}")
                # min_bot=min(a.bottom,b.bottom)
                # #print(f"Min Bot:{min_bot}")
                # max_bot=max(a.bottom,b.bottom)
                # #print(f"Max Bot:{max_bot}")
                # min_right=min(a.right,b.right)
                # #print(f"Min Right:{min_right}")
                # max_right=max(a.right,b.right)
                # #print(f"Max Right:{max_right}")
                # min_top=min(a.top,b.top)
                # #print(f"Min Top:{min_top}")
                # max_top=max(a.top,b.top)
                #print(f"Max Top:{max_top}")
                c=classification(intersecting_site[i][0])
                d=classification(intersecting_site[i][1])
                a_area=0
                b_area=0
                if c=="Polygon" and d=="Box":
                    a,a_area,b_area=calculate_areas(a,b,c,d)
                    a=a.bbox()
                    print(f"Shape 1's new bbox:{a}")
                elif c=='Box' and d=='Polygon':
                    b,b_area,a_area=calculate_areas(a,b,c,d)
                    b=b.bbox()
                    print(f"Shape 2's new bbox:{b}")
                elif c=="Polygon" and d=='Polygon':
                    a,a_area,b,b_area=calculate_areas(a,b,c,d)
                    #A will be the intersection area hence the a_area will be the intersection area
                    a=a.bbox()
                    #B will be the union area hence the b_area will be the union area
                    b=b.bbox()
                else:
                    a_area,b_area=calculate_areas(a,b,c,d)
                    min_left=min(a.left,b.left)
                    max_left=max(a.left,b.left)
                    min_bot=min(a.bottom,b.bottom)
                    max_bot=max(a.bottom,b.bottom)
                    min_right=min(a.right,b.right)
                    max_right=max(a.right,b.right)
                    min_top=min(a.top,b.top)
                    max_top=max(a.top,b.top)
                    effective_width=(min_right-max_left)
                    effective_height=(min_top-max_bot)
                    effective_area=effective_width*effective_height
                    ineffective_width=(max_right-min_left)
                    ineffective_height=(max_top-min_bot)
                    ineffective_area=(ineffective_width*ineffective_height)-effective_area
                print("Passed the reassignment of bounding box/area calculations for the box")
                # width=(min_right-max_left)
                # height=(min_top-max_bot)
                effective_area=min(a_area,b_area)
                x_left=a.left-b.left
                x_right=a.right-b.right
                y_bot=a.bottom-b.bottom
                y_top=a.top-b.top
                ineffective_area=max(a_area,b_area)-effective_area
                print(f"Ineffective area:{ineffective_area}")
                x=(x_left+x_right)/2
                y=(y_bot+y_top)/2  
                site=["OM",effective_area,c,d,x_left,x_right,y_bot,y_top,ineffective_area]#intersecting_site[i][0],intersecting_site[i][1]] need to get the shape of these to ensure they are not the same
                classify_sites.append([site,a,b])
                total_offsetmatch+=1
                if site in unique_sites:
                    print(f"Have seen this offset match site:{site} before")
                    place=0
                    for items in unique_sites:
                        if site==items:
                            break
                        else:
                            place+=1
                    unique_sites_dict[place]['Similar Sites']+=1
                    print(f"Here is the site we incremented{unique_sites_dict[place]}")
                else:
                    unique_sites.append(site)
                    unique_sites_dict[count]={"Type Match:":"Offset Match","Shape 1 type:":c,"Shape 1 bounds:":a,"Shape 2 type":d,"Shape 2 bounds:":b, "Area of Intersection:":effective_area, 'Similar Sites':0}
                    sites_visited1.append(a)
                    sites_visited2.append(b)
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

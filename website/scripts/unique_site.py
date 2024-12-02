import pya
from os import listdir
from os.path import join, isfile
from json import loads,dumps,load
import ast
import klayout.db as db
from shutil import move

def convert_to_dict_and_keys(input_dict):
    for key, value in list(input_dict.items()):
        # Convert the key to an integer
        int_key = int(key)
        value = value.replace(";", ",")
        # Safely evaluate the string to convert it to a dictionary
        input_dict[int_key] = ast.literal_eval(value)
        # Remove the old string key
        del input_dict[key]
    return input_dict
#Write diction to a JSON file 
#Diction can then be read from JSON file
def unique_pictures(gds_files_path, diction, layer_properties, width=1000, height=1000):
    print("In Unique pictures")
    print(f'GDS Fp:{gds_files_path}')
    with open(diction,'r') as file:
        values=load(file)
    #print(values)
    #print(f"Diction:{values}")
    # print("In unique sites")
    visible_layer=[(11,0),(110,0)]
    folderpath='images'
    app = pya.Application.instance()
    mw = app.main_window()
    files = [join(gds_files_path, name) for name in listdir(gds_files_path) if isfile(join(gds_files_path, name)) and name.endswith('.gds')][0]
    print(files)
    mw.load_layout(files,0)
    lv=mw.current_view()
    layout=db.Layout()
    layout.read(files)
    Units=layout.dbu
    print(f"The DBU for the layout is:{Units}")
    #lv.save_image("Whole.png",width,height)
    #print(type(values))
    unique_diction=values['List_of_unique_bonding_site']
    #print(f"Unique Diction:{unique_diction}")
    #print(unique_diction.keys())
    unique_diction=convert_to_dict_and_keys(unique_diction)
    #print(unique_diction.keys())
    #print(unique_diction)
    print("Printing Unique Sites via Indexes")
    count=1
    for layerProperties in lv.each_layer():          #loop through all layer and make them visible if they are in the visible_layer array 
        layerProperties.visible = ((layerProperties.source_layer, layerProperties.source_datatype) in visible_layer)
    for layerProperties in lv.each_layer():
        print(f"Layer {layerProperties.source_layer} visibility: {layerProperties.visible}")
    for item in unique_diction.keys():
        object_bound1=unique_diction[item]["Shape 1 bounds:"]
        object_bound2=unique_diction[item]["Shape 2 bounds:"]
        a1,a2,a3,a4=object_bound1
        b1,b2,b3,b4=object_bound2
        # print(f"Object1 bounds:{object_bound1}, Object2 bounds:{object_bound2}")
        x1=min(a1,b1)
        y1=min(a2,b2)
        x2=max(a3,b3)
        y2=max(a4,b4)
        # print(f'X1:{x1}')
        # print(f'Y1:{y1}')
        # print(f'X2:{x2}')
        # print(f'Y2:{y2}')
        tol=2
        x1-=tol
        y1-=tol
        x2+=tol
        y2+=tol
        # print("Tolerance Application:")
        # print(f'X1:{x1}')
        # print(f'Y1:{y1}')
        # print(f'X2:{x2}')
        # print(f'Y2:{y2}')
        scale_factor=0.5
        # print(f'Scale Factor:{scale_factor}')
        box_width = (x2 - x1) * scale_factor
        box_height = (y2 - y1) * scale_factor
        # print(f'Box Width:{box_width}, Box Height:{box_height}')
        zoom_pos = pya.DBox(x1 - box_width / 2, y1 - box_height / 2, x2 + box_width / 2, y2 + box_height / 2)
        # print(f'Zoom Pos:{zoom_pos}')
        a=zoom_pos.top*Units
        b=zoom_pos.right*Units
        c=zoom_pos.left*Units
        d=zoom_pos.bottom*Units
        # print("Database Units Application:")
        # print(f'X1:{c}')
        # print(f'Y1:{d}')
        # print(f'X2:{b}')
        # print(f'Y2:{a}')
        zoom_position=pya.DBox(c,d,b,a)
        print("Zooming into box:", zoom_position)
        lv.zoom_box(zoom_position)
        lv.save_image_with_options(f"unique_site{count}.png",1000,1000)
        move(f"C:\\Users\\aneal\\SiClarity\\SiBond-github\\siBond\\website\\unique_site{count}.png","C:\\Users\\aneal\\SiClarity\\SiBond-github\\siBond\\website\\scripts\\images")
        count+=1
    print("Exiting Unique Site")
    lv.close()

if __name__ == '__main__':
    #global gds_folder,diction,layer_properties
    unique_pictures(gds_folder,diction,None)

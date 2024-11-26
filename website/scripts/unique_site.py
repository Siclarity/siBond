import pya
from os import listdir
from os.path import join, isfile
from json import loads,dumps
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

def unique_pictures(gds_files_path, diction, layer_properties, width=1000, height=1000):
    print("In Unique pictures")
    print(f'GDS Fp:{gds_files_path}')
    values=loads(diction)
    #print(f"Diction:{values}")
    # print("In unique sites")
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
    unique_diction=values['List_of_unique_bonding_site']
    print(f"Unique Diction:{unique_diction}")
    print(unique_diction.keys())
    unique_diction=convert_to_dict_and_keys(unique_diction)
    print(unique_diction.keys())
    print(unique_diction)
    print("Printing Unique Sites via Indexes")
    count=1
    # for layerProperties in lv.each_layer():          #loop through all layer and make them visible
    #     layerProperties.visible = (layerProperties.source_layer, layerProperties.source_datatype)
    # for layerProperties in lv.each_layer():
    #     print(f"Layer {layerProperties.source_layer} visibility: {layerProperties.visible}")
    for item in unique_diction.keys():
        object_bound1=unique_diction[item]["Shape 1 bounds:"]
        object_bound2=unique_diction[item]["Shape 2 bounds:"]
        a1,a2,a3,a4=object_bound1
        b1,b2,b3,b4=object_bound2
        x1=min(a1,b1)
        y1=min(a2,b2)
        x2=max(a3,b3)
        y2=max(a4,b4)
        tol=2
        x1-=tol
        y1-=tol
        x2+=tol
        y2+=tol
        scale_factor=0.5
        box_width = (x2 - x1) * scale_factor
        box_height = (y2 - y1) * scale_factor
        zoom_pos = pya.DBox(x1 - box_width / 2, y1 - box_height / 2, x2 + box_width / 2, y2 + box_height / 2)
        zoom_pos.right*=Units
        zoom_pos.left*=Units
        zoom_pos.bottom*=Units
        zoom_pos.top*=Units
        print("Zooming into box:", zoom_pos)
        lv.zoom_box(zoom_pos)
        lv.save_image_with_options(f"unique_site{count}.png",1000,1000)
        move(f"C:\\Users\\aneal\\SiClarity\\SiBond-github\\siBond\\website\\unique_site{count}.png","C:\\Users\\aneal\\SiClarity\\SiBond-github\\siBond\\website\\scripts\\images")
        count+=1
    print("Exiting Unique Site")


if __name__ == '__main__':
    #global gds_folder,diction,layer_properties
    unique_pictures(gds_folder,diction,None)

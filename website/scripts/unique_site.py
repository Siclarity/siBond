print("unique_site.py script started")
import pya
from os import listdir
from os.path import join, isfile
from json import loads,dumps
def unique_pictures(gds_files_path, diction, layer_properties, width=1000, height=1000):
    print("In unique sites")
    app = pya.Application.instance()
    mw = app.main_window()
    files = [join(gds_files_path, name) for name in listdir(gds_files_path) if isfile(join(gds_files_path, name)) and name.endswith('.gds')][0]
    folderpath='images'
    initial=dumps(diction)
    site=loads(initial)
    unique_diction=site['List_of_unique_bonding_site']
    print(unique_diction)
    return
    #image_file_path=os.path.join(folderpath,f'snapshop{count}.png')
    # for file in files:
    #     mw.load_layout(file, 0)
    #     lv = mw.current_view()
        # lv.load_layer_props(layer_properties)
        # out = file.replace('gds','png')
        # print(out)
        # lv.save_image(out, width, height)

if __name__ == '__main__':
    #global gds_folder,diction,layer_properties
    unique_pictures(gds_folder,diction,None)

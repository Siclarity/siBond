import pya
from os import listdir,getcwd,remove
from os.path import join, isfile,exists
from json import loads,dumps,load
import ast
import klayout.db as db
from shutil import move

def mod_layers(gds_files_path, layer, layer_properties, width=1000, height=1000):
    #print(f"Layer parameter:{layer}")
    visible_layer=ast.literal_eval(layer)
    #print(f"Visible Layer in layer modifier:{visible_layer}")
    app = pya.Application.instance()
    mw = app.main_window()
    files = [join(gds_files_path, name) for name in listdir(gds_files_path) if isfile(join(gds_files_path, name)) and name.endswith('.gds')][0]
    #print(files)
    mw.load_layout(files,0)
    lv=mw.current_view()
    layout=db.Layout()
    layout.read(files)
    l=[]
    for layerProperties in lv.each_layer():          #loop through all layer and make them visible if they are in the visible_layer array 
        layerProperties.visible = ((layerProperties.source_layer, layerProperties.source_datatype) in visible_layer)
        #print(f"Layer {layerProperties.source_layer} visibility: {layerProperties.visible}")
        l.append((layerProperties.source_layer, layerProperties.source_datatype))
    #print(l)
    cwd=getcwd()
    # print(cwd)
    filename=[join(gds_files_path, name) for name in listdir(gds_files_path) if isfile(join(gds_files_path, name)) and name.endswith('.png')]
    for files in filename:
        if files=='sample.png':
            continue
        else:
            filename=files.split('\\')[-1]
    print(f"filename:{filename}")
    #filename=files.split('\\')[-1]
    #print(f'Filename:{filename}')
    #print(f"Last File name:{filename}")
    #lv.save_image(f"{filename}1.png",width,height)
    #This should overwrite the file.png that exists in the uploads folder
    
    directory_upload=join(cwd,'uploads')
    print(f"Direct:{directory_upload}")
    # if exists(directory_upload):
    #     print('Uploads exists')
    # Save the image with an absolute path
    #filename = join(cwd, filename)
    lv.save_image(filename, width, height)
    directory_upload=join(directory_upload,filename)
    print(f"Dest:{directory_upload}")
    if exists(directory_upload):
        remove(directory_upload)
        print("File Deleted")
    # Move the image to the uploads directory
    move(filename, directory_upload)

    print(f"File moved to: {directory_upload}")
 

    # lv.zoom_fit()
    # filename=files.split(0)
    # print(filename)

if __name__ == '__main__':
    global gds_folder,layer,layer_properties
    mod_layers(gds_folder,layer,None)

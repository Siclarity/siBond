import pya
from os import listdir
from os.path import join, isfile
from json import loads,dumps,load

def retrieve_layers(gds_files_path):
    # print("In retrieve Layers")
    app = pya.Application.instance()
    mw = app.main_window()
    files = [join(gds_files_path, name) for name in listdir(gds_files_path) if isfile(join(gds_files_path, name)) and name.endswith('.gds')][0]
    #print(files)
    mw.load_layout(files,0)
    layout=mw.current_view()
    # List of layers in the GDS file
    layers = []
    # print("Before the for")
    # Loop through the layers in the layout and collect them
    for layerProperties in layout.each_layer():
        # print(f"Layer Properties: {layerProperties}")
        # Collect layer information: layer number and datatype
        try:
            layer_info = {
                'layer': layerProperties.source_layer,  # Layer number (integer)
                'datatype': layerProperties.source_datatype,  # Datatype (integer)
                'name': f"Layer {layerProperties.source_layer}-{layerProperties.source_datatype}"  # Layer name as a combination of layer and datatype
            }
            layers.append(layer_info)
        except IndexError as e:
            print(f"Error accessing layerProperties: {layerProperties}. Exception: {e}")
    lay_json=dumps(layers)
    #print(f"{lay_json}")
    return lay_json

if __name__ == '__main__':
    global gds_files_path
    # Get the path of the GDS file from command line argument
    layers=retrieve_layers(gds_files_path)
    print(layers)

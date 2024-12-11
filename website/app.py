from flask import Flask,render_template,request,jsonify,send_from_directory
from os import listdir, system, makedirs, getcwd, path, remove
from os.path import isfile, join, isdir, exists
from scripts.thumbnails import gds_to_image_klayout
from scripts.get_layers import retrieve_layers
import shutil
import pya
from scripts.bondSearch_Flask import search
from scripts.unique_site import unique_pictures
from scripts.layer_modifier import mod_layers
from json import dumps, dump
import json
import subprocess
# from mesh_Flask_gen import *
app = Flask(__name__)

Uploaded_GDS='uploads'
app.config['Uploaded_GDS']=Uploaded_GDS 
makedirs(Uploaded_GDS, exist_ok=True)

def clear_folder(folder_path):
    # Check if the folder exists
    if path.exists(folder_path):
        # Iterate over all the files and subdirectories in the folder
        for filename in listdir(folder_path):
            file_path = path.join(folder_path, filename)
            if filename=='sample.png':
                continue
            # Check if it's a file or directory
            if path.isfile(file_path):
                remove(file_path)  # Delete file
            elif path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete directory and its contents
        print(f"Folder {folder_path} has been cleared.")
    else:
        print(f"Folder {folder_path} does not exist.")
cwd=getcwd()
IMAGE_FOLDER=f'{cwd}/scripts/images'
app.config["IMAGE_FOLDER"]=IMAGE_FOLDER

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/gds',methods=['GET','POST'])
def gds():
     # List all files in the upload folder
    files_in_folder = listdir(app.config['Uploaded_GDS'])

    # Find the first .png file in the folder
    image_filename = None
    for filename in files_in_folder:
        print(filename)
        if filename.endswith('.png') and filename!='sample.png':
            image_filename = filename
            #image_filename=f'uploads\\{image_filename}'
            break  # Exit loop after finding the first .png file

    # If no .png file is found, handle the case where the folder is empty or has no .png files
    if not image_filename:
        image_filename = "sample.png"  # You can set this to a default value or leave it as None
    print("GDS.html:",image_filename)
    # Pass the image filename (or None) to the template
    if request.method=='POST':
        return jsonify({'image_filename':image_filename})
    else:
        return render_template('gds.html',image_filename=image_filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Serve the file from the uploads folder
    print("Serving:",filename)
    return send_from_directory(app.config['Uploaded_GDS'], filename)

@app.route('/getFile',methods=['GET','POST'])
def getFile():
    if request.method=='GET':
       return jsonify({"success": True})
    if request.method == 'POST':
        # print("request:",request.get_json())
        # data=request.get_json()
        # print(data)
        # if 'file' not in data:
        if 'file' not in request.files:
            #return jsonify({'error': 'No file part'})
            print("Error: No file part"),400
        #file=data['file']
        file=request.files['file']
        #if there is no name for the file
        print(file)
        #filename=file.split('\\')[-1]
        print(file.filename)
        if file.filename == '':
            #return jsonify({'error':'No selected file'})
            print("Error:There is no file selected")
            return jsonify({'error':'No selected file'}),400
        #if there is a file
        filename=file.filename
        if filename:
            # Example usage:
            folder = f'{cwd}\\uploads'
            clear_folder(folder)
            images=f'{cwd}\\scripts\\images'
            clear_folder(images)
            #set the filename variable equal to the name of the file
            #ilename = file
            filepath = path.join(app.config['Uploaded_GDS'], filename)
            print(filepath)
            #runs into error here with the file save as file is a string and needs to be a file not string
            try:
                file.save(filepath)
                #return jsonify({'success':'File uploaded successfully'})
                print("Successfully uploaded:",filename)
                #cwd = getcwd()
                system(f"C:\\Users\\aneal\\AppData\\Roaming\\KLayout\\klayout_app.exe -z -r {cwd}/scripts/thumbnails.py  -rd gds_folder={cwd}\\uploads")
                return jsonify({"success": "File uploaded successfully","filename":filename, "Image status:":"Loading..."})

            except Exception as e:
                print("Error while saving file:", e)
                return jsonify({"error": "File upload failed"}), 500
            #run bondsearch here
    #return render_template('gds.html')
        #return jsonify({"success": False})

@app.route('/search', methods=["POST"])
def search_sites():
    
    selected_layers = request.json.get('layers', [])
    print("Selected layers:", selected_layers)
    # Ensure selected_layers is a list of dictionaries
    if isinstance(selected_layers, list):
        # Log each element of selected_layers to verify the structure
        for i, layer in enumerate(selected_layers):
            print(f"Layer {i}: {layer}")
    else:
        print("Selected layers is not a list")
    # Convert selected layers into a list of tuples (layer, datatype)
    try:
        visible_layer = [
            (int(layer.split('-')[0]), int(layer.split('-')[1]))  # Split on '-' and convert to integers
            for layer in selected_layers
        ]
        print(f"Formatted visible layers: {visible_layer}")
        visible_layer_str = str(visible_layer)
        print(f"Stringified visible layers: {visible_layer_str}")
    except Exception as e:
        print("Error while formatting visible layers:", e)
    files_in_folder = listdir(app.config['Uploaded_GDS'])
    # Find the .gds file in the folder
    gds_filename = None
    for filename in files_in_folder:
        if filename.endswith('.gds'):
            gds_filename=f"uploads/{filename}"
            c=search(gds_filename, visible_layer)
            #print(f'C:{c}')
            print(type(c))
            # diction_serialized=dumps(c)
            # diction_serialized = diction_serialized.replace('"', '\\"') 
            with open("information.json","w") as outfile:
                dump(c,outfile)
            #print(type(diction_serialized))
            images=f'{cwd}\\scripts\\images'
            clear_folder(images)
            print("Entering Unique_site")
            #print(f"Arguments passed:\n gds_folder={cwd}\\uploads \n diction={diction_serialized}")

            cm=f'C:\\Users\\aneal\\AppData\\Roaming\\KLayout\\klayout_app.exe -z -r {cwd}/scripts/unique_site.py  -rd gds_folder={cwd}\\uploads  -rd diction={cwd}\\information.json -rd layer="{visible_layer_str}"'
            #print(f"CM:{cm}")
            # test=system(cm)
            result=subprocess.run(cm,shell=True,capture_output=True,text=True)
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            print(f"Exiting Unique_Site:{result.returncode}")
    print(c)
    return jsonify({"Result":c})


@app.route('/scripts/images/<filename>')
def unique_images(filename):
    print(f"Gallery:{filename}")
    return send_from_directory(IMAGE_FOLDER, filename)
@app.route('/gallery')
def gallery():
    # Get all image filenames in the directory
    images = [f for f in listdir(IMAGE_FOLDER) if f.lower().endswith(('.png'))]
    if not images:
        return jsonify([])
    return jsonify(images)

# Endpoint to get the available layers from the GDS file
@app.route('/get_layers', methods=['GET'])
def get_layers():
    try:
        # Get all GDS files in the specified directory
        gds_files = [f for f in listdir(Uploaded_GDS) if f.endswith('.gds')]
        if not gds_files:
            return jsonify({'status': 'error', 'message': 'No GDS files found in the directory'}), 400


        # Build the command to execute the KLayout script
        cm = f'C:\\Users\\aneal\\AppData\\Roaming\\KLayout\\klayout_app.exe -z -r {cwd}/scripts/get_layers.py -rd gds_files_path={cwd}\\uploads'

        # Run the command and capture the output
        result = subprocess.run(cm, shell=True, capture_output=True, text=True)
        # Log the result
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        print(f"Return Code: {result.returncode}")
        # Check if the command was successful
        if result.returncode != 0:
            return jsonify({'status': 'error', 'message': 'Error running KLayout script', 'details': result.stderr}), 500

        # Assuming that the KLayout script returns the layers in a suitable format (e.g., JSON)
        print(f"Layers outside the python file:{result.stdout}")
        layers = result.stdout.strip()
        print(f"Strip the layers outside the python file:{layers}")
        # Here, you should process the 'layers' string if needed.
        # For now, we assume it is already a JSON string (adjust this as needed).
        try:
            layers_data = json.loads(layers)  # Convert the output to a Python object (list or dict)
        except json.JSONDecodeError as e:
            return jsonify({'status': 'error', 'message': f'Error parsing layers: {str(e)}'}), 500

        return jsonify(layers_data)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Endpoint to update the thumbnail based on selected layers
@app.route('/update_thumbnail', methods=['POST'])
def update_thumbnail():
    try:
        selected_layers = request.json.get('layers', [])
        
        if not selected_layers:
            return jsonify({'status': 'error', 'message': 'No layers selected'}), 400

        print("Selected layers:", selected_layers)

        # Convert selected layers into a list of tuples (layer, datatype)
        visible_layer = [(int(layer['layer']), int(layer['datatype'])) for layer in selected_layers]
        print(f"Formatted visible layers: {visible_layer}")
        visible_layer_str = str(visible_layer)
        cm = f'C:\\Users\\aneal\\AppData\\Roaming\\KLayout\\klayout_app.exe -z -r {cwd}/scripts/layer_modifier.py -rd gds_folder={cwd}\\uploads -rd layer="{visible_layer_str}"'

        # Run the KLayout command
        result = subprocess.run(cm, shell=True, capture_output=True)

        # Log the result
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        print(f"Return Code: {result.returncode}")

        if result.returncode != 0:
            return jsonify({'status': 'error', 'message': 'Error running KLayout script', 'details': result.stderr.decode()}), 500

        return jsonify({'status': 'success', 'message': 'Thumbnail updated successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/generate_gds_mesh', methods=['POST'])
# def meshGenerate_gds():
#     data = request.json  # Get the incoming JSON data from the client
#     print("Received data:", data)
#     #writing the data that the user inputs and the backend data to a file which can be used for the python code, this file can be used for the new mesh python file
#     with open("bonding_sites.json","w") as outfile:
#         dump(data,outfile)
#     # Return a response (you can return results if needed, or just a success message)
#     return jsonify({'message': 'Success'})  # This will then forward the user to the meshGDS page

@app.route('/mesh',methods=["GET","POST"])
def temp():
    if request.method == 'POST':
        try:
            data = request.get_json()  # gets the JSON
            print(f'Data Received: {data}')
            return render_template('mesh.html', data=data)
        except Exception as e:
            print(f'Error parsing JSON: {e}')
            return "Error parsing JSON", 400  # Send a proper error response
    else:
        return render_template('mesh.html')
@app.route('/meshGenerator')
def meshGenerator():
        return render_template('meshGenerator.html')
# @app.route('/meshGenerator',methods=['GET','POST'])
# def meshGenerator():
#   if request.method=='POST':
#       SiO2w=request.form.get('sio2w')
#       print(SiO2w)
#   return render_template('meshGenerator.html')
if __name__ =='__main__':
    app.run(debug=True,host='0.0.0.0')
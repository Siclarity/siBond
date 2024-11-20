from flask import Flask,render_template,request,jsonify,send_from_directory
from os import listdir, system, makedirs, getcwd, path, remove
from os.path import isfile, join, isdir, exists
from scripts.thumbnails import gds_to_image_klayout
import shutil
import pya
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
            
            # Check if it's a file or directory
            if path.isfile(file_path):
                remove(file_path)  # Delete file
            elif path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete directory and its contents
        print(f"Folder {folder_path} has been cleared.")
    else:
        print(f"Folder {folder_path} does not exist.")
cwd=getcwd()
# Example usage:
folder = f'{cwd}\\uploads'

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
        if filename.endswith('.png'):
            image_filename = filename
            #image_filename=f'uploads\\{image_filename}'
            break  # Exit loop after finding the first .png file

    # If no .png file is found, handle the case where the folder is empty or has no .png files
    if not image_filename:
        image_filename = None  # You can set this to a default value or leave it as None
    print(image_filename)
    # Pass the image filename (or None) to the template
    return render_template('gds.html',image_filename=image_filename)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    # Serve the file from the uploads folder
    print(filename)
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
            clear_folder(folder)
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
                return jsonify({"success": "File uploaded successfully","filename":filename, "Image status:":"Please Refresh your browser to see the image of the GDS file"})
            except Exception as e:
                print("Error while saving file:", e)
                return jsonify({"error": "File upload failed"}), 500
            #run bondsearch here
    #return render_template('gds.html')
        #return jsonify({"success": False})
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
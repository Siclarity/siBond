from flask import Flask,render_template,request,jsonify
import os
from os import listdir
from os.path import isfile, join

# from mesh_Flask_gen import *
app = Flask(__name__)

Uploaded_GDS='uploads'
app.config['Uploaded_GDS']=Uploaded_GDS 
os.makedirs(Uploaded_GDS, exist_ok=True)

@app.route("/")
def home():
    return render_template('index.html')
@app.route('/gds',methods=['GET','POST'])
def gds():
    return render_template('gds.html')

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
            #set the filename variable equal to the name of the file
            #ilename = file
            filepath = os.path.join(app.config['Uploaded_GDS'], filename)
            #runs into error here with the file save as file is a string and needs to be a file not string
            try:
                file.save(filepath)
                #return jsonify({'success':'File uploaded successfully'})
                print("Successfully uploaded:",filename)
                return jsonify({"success": "File uploaded successfully","filename":filename})
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
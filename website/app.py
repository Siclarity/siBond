from flask import Flask,render_template
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')
@app.route('/gds')
def gds():
    return render_template('gds.html')
@app.route('/meshGenerator')
def meshGenerator():
    return render_template('meshGenerator.html')

if __name__ =='__main__':
    app.run(debug=True,host='0.0.0.0')
from flask import Flask, render_template, request, flash, redirect, send_from_directory, send_file, jsonify
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename
import json
import yaml
import requests
import secrets
import os
import to_csv
from pathlib import Path


app = Flask(__name__)
app.secret_key = secrets.token_hex().encode('utf-8')

UPLOAD_FOLDER = 'static/scans'
ALLOWED_EXTENSIONS = {'json'}
HOME = str(Path.home())

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

csrf = CSRFProtect(app)

severity_grade = {
    "info":0,
    "low":1,
    "medium":2,
    "critical":3
}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sort_by_name(elem):
    try:
        return elem['info']['name']
    except:
        return elem['id']
    
def sort_by_severity(elem):
    return severity_grade[elem['info']['severity']]

def sort_by_techno(elem):
    return elem['type']


@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/download/<file>')
def download_report(file):
	to_csv.convert_json('static/scans/'+file)
	return send_file('static/scans/'+file.split('.json')[0]+".csv", as_attachment=True)

@app.route('/delete_file/<file>')
def delete_file(file):
    os.remove(f'static/scans/{file}')
    return redirect('/scan')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        # check if the post request has the file part
        if 'rapport' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['rapport']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Fichier mis en ligne')
        return redirect('/upload')

@app.route('/to-json', methods=['POST','GET'])
def to_json():
    return jsonify(description=to_csv.get_description('/nuclei-templates/'+request.json['path'].split('nuclei-templates/')[-1]))

@app.route('/scan')
def scan():
	if 'file' in request.args:
		if request.args.get('file').endswith('.json'):
			with open('static/scans/'+request.args.get('file'),'r') as f:
				data = json.load(f)
			severity_dict = {
				"info": "info",
				"low": "primary",
				"medium": "warning",
				"high": "danger",
				"critical": "dark"
					}
			if 'sort' in request.args:
				sort = request.args.get('sort')
				if sort == 'name':
					data.sort(key=sort_by_name)
				elif sort == 'techno':
					data.sort(key=sort_by_techno)
				elif sort == 'severity':
					data.sort(key=sort_by_severity,reverse=True)
			return render_template('scan.html', data=data,  severity_dict=severity_dict, file=request.args.get('file'))
		flash('Fichier innexistant')
		return redirect('/scan')
	else:
		file_list = os.listdir('static/scans')
		return render_template('file_list.html', files=[x for x in file_list if x.endswith('.json')])


if __name__ == "__main__":
    app.run(debug=True)

import json
import csv
import yaml
from pathlib import Path

HOME = str(Path.home())

def read_file(path):
	try:
		with open(path, 'r') as f:
			data = json.load(f)
		return data
	except Exception as e:
		print('FILE ERROR (to_csv.py) :'+ str(e))
		return []
	
	
def description_from_path(path):
	try:
		with open(path,'r') as f:
			res = f.read()
		
		data = yaml.load(res)
	except Exception as e:
		print('YAML FILE ERROR (to_csv.py)'+ str(e))
		return "No template found"
		
	if 'description' in data['info']:
		return data['info']['description']
	else:
		return "No description provided"


def convert_json(path):
	data = read_file(path)
	with open(path.split('.json')[0]+".csv",'w', newline='') as csvfile:
		fieldnames = ['Gravité', 'Template', 'tags','Description' ,'Name', 'Point de coherence']
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()
		counter = 0
		for x in data:
			print(f"PARSING line [{counter}/{len(data)}]",end="\r")
			
			description = get_description('/nuclei-templates/'+x['template-path'].split('nuclei-templates/')[-1])
			writer.writerow({"Gravité":x['info']['severity'], "Template":x['template'], "tags":x['info']['tags'], "Description":description, "Name":x['info']['name'], "Point de coherence": x["matched-at"]})
			counter+=1
			
def get_description(path):
	return description_from_path(HOME + path)
		

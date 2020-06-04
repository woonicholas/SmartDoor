from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS
import json
import ui_client

app = Flask(__name__)
CORS(app)

@app.route('/')
def home_page():
  with open('db.json', 'r') as json_file:
    with open('songs.json', 'r') as song_file:
      people = json.load(json_file)
      songs = json.load(song_file)
      return render_template("index.html", people = people['people'], songs= songs['songs'])

@app.route('/employee/<id>')
def employee_page(id):
  with open('db.json', 'r') as db:
    data = json.load(db)
    for i in data['people']:
      if i["id"] == id:
        data = i
        break
  return render_template("employee.html", employee=data)

@app.route('/select-song', methods = ['PUT'])
def select_song():
  req = request.get_json()
  with open('db.json', "r+") as json_file:
    data = json.load(json_file)
    for s in range(len(data['people'])):
      if req['id'] == data['people'][s]['id']:
        data['people'][s]['song'] = req['song']
        json_file.seek(0)
        json.dump(data, json_file,indent=2)
        json_file.truncate()
        break
  res = make_response(jsonify({"message": "OK"}), 200)
  return res

@app.route('/create_user', methods=['POST'])
def create_user():
  req = request.get_json()
  print(req)
  with open('db.json', 'r+') as json_file:
    data = json.load(json_file)
    req['id'] = str(int(data['people'][len(data['people'])-1]['id']) + 1)
    data['people'].append(req)
    json_file.seek(0)
    json.dump(data, json_file,indent=2)
    json_file.truncate()
  res = make_response(jsonify({"message": "OK"}), 200)
  return res

if __name__ == "__main__":
  app.run(debug=True)
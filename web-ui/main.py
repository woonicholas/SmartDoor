from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS
import json
import ui_client
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_time_for_api():
  now = datetime.now()
  if(now.weekday() < 5):
    return '%d/%d/%d' % (8, 30, now.weekday())
  else:
    return '%d/%d/%d' % (now.hour, now.minute, now.weekday())

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
  now = datetime.now()
  enter_time = requests.get('http://35.236.46.222:8080/enter/%s/%s' % (data['name'], get_time_for_api()), 
        auth=('smartdoorcool',
              'smartdoorpass'))
  enter_prediction = json.loads(enter_time.text)
  leave_time = requests.get('http://35.236.46.222:8080/leave/%s/%s/%s/%s' % (data['name'], \
        enter_prediction['predicted_enter'][0], enter_prediction['predicted_enter'][1], now.weekday()),
        auth=('smartdoorcool',
              'smartdoorpass'))
  leave_prediction = json.loads(leave_time.text)

  predictions = dict()
  predictions['predicted_enter'] = datetime(now.year, now.month, now.day, enter_prediction['predicted_enter'][0], enter_prediction['predicted_enter'][1]).isoformat()
  predictions['predicted_leave'] = datetime(now.year, now.month, now.day, leave_prediction['leave'][0], leave_prediction['leave'][1]).isoformat()
  predictions['day_start'] = datetime(now.year,now.month, now.day, 0).isoformat()
  predictions['day_end'] = datetime(now.year,now.month, now.day, 23).isoformat()

  print(predictions)

  return render_template("employee.html", employee=data, predictions = predictions)

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
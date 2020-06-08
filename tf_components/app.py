# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
import tf
import data_maker
from flask import Flask, request, jsonify, after_this_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from base64 import b64decode
from dotenv import load_dotenv
import os


load_dotenv()
USER, PASS = os.getenv('USERNAME'), os.getenv('PASSWORD')

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["15 per minute", "1 per second"],
)
enter_model = None
leave_model = None
EPOCH = 250
#model = tf.get_model(10)

def authenticate():
    try:
        auth = b64decode(request.headers['Authorization'][5:]).decode('utf-8')
        username, password = auth.split(':')
        return USER == username and PASS == password
    except:
        return False
    

@app.before_first_request
def set_model():
    global leave_model
    leave_model = tf.train_model(EPOCH, 'leave.data', 'Enter', 'Time Spent')
    global enter_model
    enter_model = tf.train_model(EPOCH, 'enter.data', 'Supposed Enter', 'Enter')

@app.route('/')
def hello():
    return ('can predict when someone will arrive given a supposed arrival time<br>'
    'can predict when someone will leave given an arrival time'
    'valid names {}<br>'
    'valid hours: 0-23<br>'
    'valid minutes: 0-59<br>'
    'valid days: 0-6<br>'
    'http://35.236.46.222:8080/enter/name/hour/minute/day<br>'
    'http://35.236.46.222:8080/leave/name/hour/minute/day'.format(data_maker.people))

@app.route('/newdata', methods=['POST'])
def insert_data():
    '''
    body would look like this:
    {
    "data": [
        {
            "name": "Liam",
            "enter_time": 1238,
            "time_spent": 20,
            "supposed_enter_time": 1239,
            "day": 2
        },
        {
            "name": "Benjamin",
            "enter_time": 349,
            "supposed_enter_time": 355,
            "time_spent": 150,
            "day": 6
        }
    ]
    }
    '''
    if not authenticate():
        return 'Wrong Username or Password'
    try:
        data_maker.write_new_data(request.get_json()['data'])
    except Exception as e:
        return str(e)
    return 'successfully inserted data'

@app.route('/retrain')
def retrain():
    if not authenticate():
        return 'Invalid Username or Password'
    global leave_model
    leave_model = tf.get_leave_model(EPOCH)
    global enter_model
    enter_model = tf.get_enter_model(EPOCH)
    return 'successfully retrained the model'

@app.route('/enter/<name>/<int:hour>/<int:minute>/<int:day>')
def predict_enter(name, hour, minute, day):
    #return name + str(hour) + str(day)
    if not authenticate():
        return 'Invalid Username or Password'
    try:
        return tf.predict_enter(enter_model, name, hour*60 + minute, day)
    except Exception as e:
        return str(e)


@app.route('/leave/<name>/<int:hour>/<int:minute>/<int:day>')
def predict_leave(name, hour, minute, day):
    #return name + str(hour) + str(day)
    if not authenticate():
        return 'Invalid Username or Password'
    try:
        return tf.predict_leave(leave_model, name, hour*60 + minute, day)
    except Exception as e:
        return str(e)

@app.route('/attendance/<name>/<date>')
def get_attendance(name, date):
    if not authenticate():
        return 'Invalid Username or Password'
    try:
        return tf.get_attendance(name, date)
    except Exception as e:
        return str(e)

@app.route('/multiple_attendance/<name>/<dates>')
def get_multiple_attendance(name, dates):
    if not authenticate():
        return 'Invalid Username or Password'
    try:
        return tf.get_multiple_attendance(name, dates)
    except Exception as e:
        return str(e)        

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    #app.run(host='127.0.0.1', port=8080, debug=True)
    #app.run(host='34.105.53.213', port=8080, debug=True)
    #app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
        app.run(host='0.0.0.0', debug=False, use_reloader=False)
# [END gae_python38_app]

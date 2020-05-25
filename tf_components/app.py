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
from base64 import b64decode
from dotenv import load_dotenv
import os

load_dotenv()
USER, PASS = os.getenv('USERNAME'), os.getenv('PASSWORD')

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
model = None
EPOCH = 2
#model = tf.get_model(10)

def authenticate():
    auth = b64decode(request.headers['Authorization'][5:]).decode('utf-8')
    username, password = auth.split(':')
    return USER == username and PASS == password
    

@app.before_first_request
def set_model():
    global model
    model = tf.get_model(EPOCH)

@app.route('/')
def hello():
    return ('type into route url/name/enter_time/day to predict how long they will stay<br>'
    'valid names {}<br>'
    'valid hours: 0-23<br>'
    'valid minutes: 0-59<br>'
    'valid days: 0-6<br>'
    'an example: http://35.236.46.222:8080/Benjamin/5/36/2 <br>'
    'this corresponds to Benjamin arrived at 5:36am on a Tuesday'.format(data_maker.people))

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
			"day": 2
		},
		{
			"name": "Benjamin",
			"enter_time": 349,
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
    global model
    model = tf.get_model(EPOCH)
    return 'successfully retrained the model'

@app.route('/<name>/<int:hour>/<int:minute>/<int:day>')
def predict(name, hour, minute, day):
    #return name + str(hour) + str(day)
    if not authenticate():
        return 'Invalid Username or Password'
    return tf.predict_leave(model, name, hour*60 + minute, day)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
	#app.run(host='127.0.0.1', port=8080, debug=True)
	#app.run(host='34.105.53.213', port=8080, debug=True)
	#app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
        app.run(host='0.0.0.0', debug=False, use_reloader=False)
# [END gae_python38_app]

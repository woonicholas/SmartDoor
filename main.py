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
from flask import Flask

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return ('type into route url/name/enter_time/day to predict how long they will stay<br>'
    'valid names {}<br>'
    'valid times: 0-1440<br>'
    'valid days: 0-6'.format(data_maker.people))

@app.route('/<name>/<int:enter>/<int:day>')
def article(name, enter, day):
	return tf.predict_leave(name, enter, day)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
	app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_app]

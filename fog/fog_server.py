import threading
from datetime import datetime
import requests
import json
import zmq
import sys
import os

# cloud credentials
USER, PASS = os.getenv('USERNAME'),os.getenv('PASSWORD')

##imports from parent directory
sys.path.insert(0, '..')
from constants import *

allclients = set()
time_dict = dict()
songs_dict = dict()
song_map = dict()
visitor_dict = dict()
data_for_cloud = list()
people_inside = set()
client_lock = threading.Lock()
time = 0
with open('songs_db.json', 'r') as songs_db:
    songs_dict = json.load(songs_db)
    songs_db.close()
with open('song_map.json', 'r') as song_file:
    song_map = json.load(song_file)
    song_file.close()


class Visit:
    def __init__(self, name, enter_time, time_spent, day):
        self.name = name
        self.enter_time = int(enter_time)
        self.time_spent = int(time_spent)
        self.day = day


def message_clients(message):
    with client_lock:
        for i in allclients:
            i.send(message.encode())


def get_time_for_api():
    now = datetime.now()
    return '%d/%d/%d' % (now.hour, now.minute, now.weekday())

# camera Ivan outside 129123
def fog_server():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    print('Collecting updates from cameras')
    socket.bind("tcp://%s:%s" % (HOST, IN_PORT))  # sUBS to Speaker server

    socket.setsockopt_string(zmq.SUBSCRIBE, 'camera')

    pub = context.socket(zmq.PUB)
    pub.bind("tcp://%s:%s" % (HOST, OUT_PORT))  # PUBS to Speaker server

    try:
        while True:
            message = socket.recv().decode()
            splitted = message.split()
            topic = splitted[0]
            name = splitted[1]
            location = splitted[2]
            print("%s detected %s %s"%(topic, name, location))
            if topic == 'camera':
                if name not in visitor_dict:
                    visitor_dict[name] = {
                        'location': ''
                    }
                    


                if location == 'outside':
                    if visitor_dict[name]['location'] == '':
                        visitor_dict[name]['location'] = 'outside'
                    elif visitor_dict[name]['location'] == 'inside':

                        # calculate how long this person was inside for and add it to data_for_cloud
                        if name in time_dict:
                            time_entered = time_dict[name][1]
                            now = datetime.now()
                            time_exitted = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
                            data_for_cloud.append(Visit(name,
                                                        time_entered,
                                                        int((time_exitted - time_entered) / 60),
                                                        time_dict[name][3]))
                            del time_dict[name]

                        fog_pub(pub, 'speaker %s exit %s' % (name, get_time_for_api()))
                        visitor_dict[name]['location'] = 'outside'
                        

                if location == 'inside':
                    if visitor_dict[name]['location'] == '':
                        visitor_dict[name]['location'] = 'inside'
                    elif visitor_dict[name]['location'] == 'outside':

                        # save when the person entered the room in time_dict
                        if name not in time_dict:
                            l = list()
                            now = datetime.now()
                            time_entered = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
                            l.extend([name, int(time_entered), 0, datetime.today().weekday()])
                            time_dict[name] = l

                        song = ''
                        for p in songs_dict['people']:
                            if p['name'] == name:
                                song = p['song']
                        music_message = 'speaker ' + name + ' enter ' + song  # adds person's name and song_file to send to
                        music_message = music_message + ' ' + get_time_for_api()  # adds formatted datetime for cloud
                        fog_pub(pub, music_message)
                        visitor_dict[name]['location'] = 'inside'

                if len(data_for_cloud) >= 2:
                    # send the data to cloud
                    cloud_data = [{'name': x.name, 'enter_time': x.enter_time, 'time_spent': x.time_spent, 'day': x.day} for x in completed_list]
                    d = dict()
                    d['data'] = cloud_data

                    url = 'http://35.236.46.222:8080/newdata'

                    r = requests.post(url, data=json.dumps(d), auth=(USER,PASS))

                    print('Sending this to cloud: ')
                    print(json.dumps(d, indent=4))
                    print('Status Code: ' + r.status_code)

                    completed_list = list()


    except KeyboardInterrupt:
        print('Exiting Server..')


def fog_pub(pub, message):
    print(message)
    pub.send_string(message)


if __name__ == '__main__':
    fog_server()
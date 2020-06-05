import json
import random
import datetime
import numpy as np

data = {}

people = ["Preston", "Brandon", "Nick",
          "Henry", "Ivan"]


def randomTime(base, end):
    # generate random number scaled to number of minutes in a day
    # (24*60) = 1,440

    rtime = int(random.randrange(base, end))

    hours   = int(rtime/60)
    minutes = int((rtime - hours*60)/60)
    return hours, minutes, rtime

def timeToString(hours, minutes):
    # figure out AM or PM
    hours = hours%24
    if hours >= 12:
        suffix = 'PM'
        if hours > 12:
            hours = hours - 12
    else:
        suffix = 'AM'
    if hours == 0:
        hours = 12

    time_string = '%02d:%02d' % (hours, minutes)
    time_string += ' ' + suffix
    return time_string

class TimeObject():
    def __init__(self, name,
                enter_hour, enter_minute, 
                 enter_time, leave_time, day, supposed_enter_time):
        self.name = name
        self.enter_hour = enter_hour
        self.enter_minute = enter_minute
        self.enter_time = enter_time
        self.supposed_enter_time = supposed_enter_time
        self.day = day
        self.time_spent = leave_time - enter_time

def write_to_file():
    for p in people:
        data[p] = set()
        start = int(abs(random.gauss(200, 80)))
        end = int(abs(random.gauss(1000, 80)))
        stay = int(abs(random.gauss((end-start)/4, 80)))
        start, end = min(start, end), max(start, end)
        delta = int(random.uniform(-20, 20))
        for i in range(150):
            day = int(random.random()*7)
            eh, em, stime = randomTime(start, end)
            lrtime = stime + int(30 + stime+stay * (1.07 - day/40) * random.uniform(0.98, 1.02))
            supposed_enter = stime + delta + int(random.uniform(-3, 4))
            data[p].add(TimeObject(p, eh, em, stime, lrtime, day, supposed_enter))


    with open('enter.data', 'w') as file:
        for k, v in data.items():
            for i in v:
                file.write(str(i.name) + ' ')
                file.write(str(i.enter_time) + ' ')
                file.write(str(i.day) + ' ')
                file.write(str(i.supposed_enter_time) + '\n')

    with open('leave.data', 'w') as file:
        for k, v in data.items():
            for i in v:
                file.write(str(i.name) + ' ')
                file.write(str(i.enter_time) + ' ')
                file.write(str(i.day) + ' ')
                file.write(str(i.time_spent) + '\n')

'''
data: [['Emma', 329, 2, 234],
       ['Benjamin', 123, 0, 560],
       ['Liam', 429, 6, 100],
    ]
'''
def write_new_data(data):
    for i in data:
        print(i)
        with open('enter.data', 'a+') as efile:
            efile.write(str(i['name']) + ' ')
            efile.write(str(int(i['enter_time'])) + ' ')
            efile.write(str(int(i['day'])) + ' ')
            efile.write(str(int(i['supposed_enter_time'])) + '\n')
        with open('leave.data', 'a+') as lfile:
            lfile.write(str(i['name']) + ' ')
            lfile.write(str(int(i['enter_time'])) + ' ')
            lfile.write(str(int(i['day'])) + ' ')
            lfile.write(str(int(i['time_spent'])) + '\n')



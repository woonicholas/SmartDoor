import json
import random
import datetime
import numpy as np

data = {}

people = ["Liam", "Emma",
          "Noah", "Olivia",
          "Benjamin", "Charlotte",
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
				 enter_time, leave_time, day):
		self.name = name
		self.enter_hour = enter_hour
		self.enter_minute = enter_minute
		self.enter_time = enter_time
		self.day = day
		self.time_spent = leave_time - enter_time

def write_to_file():
	for p in people:
		data[p] = set()
		start = int(abs(random.gauss(200, 80)))
		end = int(abs(random.gauss(1000, 80)))
		stay = int(abs(random.gauss((end-start)/4, 80)))
		start, end = min(start, end), max(start, end)
		for i in range(100):
			day = int(random.random()*7)
			eh, em, stime = randomTime(start, end)
			lrtime = stime + int(30 + stime+stay * (1.07 - day/40) * random.uniform(0.98, 1.02))
			data[p].add(TimeObject(p, eh, em, stime, lrtime, day))


	with open('time.data', 'w') as file:
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
    with open('time.data', 'a+') as file:
        for i in data:
            print(i.items())
            file.write(str(i['name']) + ' ')
            file.write(str(int(i['enter_time'])) + ' ')
            file.write(str(int(i['day'])) + ' ')
            file.write(str(int(i['time_spent'])) + '\n')



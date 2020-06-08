# learned tf with https://www.tensorflow.org/tutorials/keras/regression
import pathlib

#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import json
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers

#import tensorflow_docs as tfdocs
#import tensorflow_docs.modeling

NEW_FILE = False

class EpochDots(tf.keras.callbacks.Callback):
  """A simple callback that prints a "." every epoch, with occasional reports.
  Args:
    report_every: How many epochs between full reports
    dot_every: How many epochs between dots.
  """

  def __init__(self, report_every=100, dot_every=1):
    self.report_every = report_every
    self.dot_every = dot_every

  def on_epoch_end(self, epoch, logs):
    if epoch % self.report_every == 0:
      print()
      print('Epoch: {:d}, '.format(epoch), end='')
      for name, value in sorted(logs.items()):
        print('{}:{:0.4f}'.format(name, value), end=',  ')
      print()

    if epoch % self.dot_every == 0:
      print('.', end='')


#dataset_path = keras.utils.get_file("auto-mpg.data", "http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data")

import data_maker
import os

norm_dict = dict()

def train_model(epoch, path, diff, ppram):
    if NEW_FILE or not os.path.exists(path):
        data_maker.write_to_file()
    
    column_names = ['Name', 'Day', diff, ppram]
    raw_dataset = pd.read_csv(path, names=column_names,
                          na_values = "?", comment='\t',
                          sep=" ", skipinitialspace=True)
    dataset = raw_dataset.copy()
    dataset.isna().sum()
    dataset = dataset.dropna()
    dataset = pd.get_dummies(dataset, prefix='', prefix_sep='')
    train_dataset = dataset.sample(frac=0.8,random_state=0)
    test_dataset = dataset.drop(train_dataset.index)

    train_stats = train_dataset.describe()

    global norm_dict
    norm_dict[ppram] = (train_stats[ppram].std(), train_stats[ppram].mean())
    train_stats.pop(ppram)
    train_stats = train_stats.transpose()

    norm_dict[path] = train_stats

    train_labels = train_dataset.pop(ppram)
    test_labels = test_dataset.pop(ppram)

    global norm
    def norm(x, path):
      return (x - norm_dict[path]['mean']) / norm_dict[path]['std']
    global denorm
    def denorm(x, key):
      #print('std', norm_dict[key][0])
      return (x - norm_dict[key][1]) / (norm_dict[key][0]/4)
    normed_train_data = norm(train_dataset, path)
    normed_test_data = norm(test_dataset, path)

    def build_model():
      model = keras.Sequential([
        layers.Dense(64, activation='relu', input_shape=[len(train_dataset.keys())]),
        layers.Dense(64, activation='relu'),
        layers.Dense(1)
      ])
      optimizer = tf.keras.optimizers.RMSprop(0.001)
      model.compile(loss='mse',
                    optimizer=optimizer,
                    metrics=['mae', 'mse'])
      return model

    model = build_model()
    model.summary()
    example_batch = normed_train_data[:10]
    example_result = model.predict(example_batch)

    EPOCHS = epoch
    history = model.fit(
      normed_train_data, train_labels,
      epochs=EPOCHS, validation_split = 0.2, verbose=0,
      callbacks=[EpochDots()])
    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch
    hist.tail()
    print()

    #test_predictions = model.predict(normed_test_data).flatten()
    return model

def predict_leave(model, name, enter, day):
    if day < 0 or day > 6:
        return '{} is not a valid day of the week, please put 0-6'.format(day)
    if name not in data_maker.people:
        return ("we don't have enough data for {} yet<br>"
                "here's a list of people we currently have {}".format(name, data_maker.people))
    weekday = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']
    my_dataset = pd.DataFrame(data={'Name': [name],
                                  'Enter': [enter],
                                  'Day': [day]})
    my_dataset = pd.get_dummies(my_dataset, prefix='', prefix_sep='')
    normed_data = norm(my_dataset, 'leave.data').fillna(value=0)
    my_prediction = model.predict([normed_data]).flatten()
    leave = denorm([int(x) for x in my_prediction][0], 'Time Spent') + enter
    return '{} came in at {} on a {} and is predicted to leave at {}'.format(
        name,
        data_maker.timeToString(enter//60, enter%60),
        weekday[day],
        data_maker.timeToString(leave//60, leave%60))

def predict_enter(model, name, supposed_enter, day):
    if day < 0 or day > 6:
        return '{} is not a valid day of the week, please put 0-6'.format(day)
    if name not in data_maker.people:
        return ("we don't have enough data for {} yet<br>"
                "here's a list of people we currently have {}".format(name, data_maker.people))
    weekday = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']
    my_dataset = pd.DataFrame(data={'Name': [name],
                                  'Supposed Enter': [supposed_enter],
                                  'Day': [day]})
    my_dataset = pd.get_dummies(my_dataset, prefix='', prefix_sep='')
    normed_data = norm(my_dataset, 'enter.data').fillna(value=0)
    my_prediction = model.predict([normed_data]).flatten()
    enter = denorm([int(x) for x in my_prediction][0], 'Enter')
    return '{} is scheduled to come in at {} on a {} and is predicted to come in at {}'.format(
        name,
        data_maker.timeToString(supposed_enter//60, supposed_enter%60),
        weekday[day],
        data_maker.timeToString(enter//60, enter%60))

def get_attendance(name, date):
    if name not in data_maker.people:
        return ("we don't have enough data for {} yet<br>"
                "here's a list of people we currently have {}".format(name, data_maker.people))  

    ret = None 

    with open('attendance.json', 'r') as attendance_file:
        data = json.load(attendance_file)
        record = data["history"][name]
        for attendance in record["attendance"]:
            if (attendance["date"] == date):
                enter_time = attendance["enter_time"]
                leave_time = attendance["leave_time"]
                ret = {
                    'name' : name,
                    'enter_time': data_maker.timeToString(enter_time//60, enter_time%60),
                    'leave_time': data_maker.timeToString(leave_time//60, leave_time%60)
                }
    if (ret != None):
        print(ret)
        return json.dumps(ret)
    else:
        print("Date is either invalid or no record for requested date")
        return("Date is either invalid or no record for requested date")


## dates should be an array of strings
def get_multiple_attendance(name, dates):
    if name not in data_maker.people:
        return ("we don't have enough data for {} yet<br>"
                "here's a list of people we currently have {}".format(name, data_maker.people))  

    ret = {}  

    with open('attendance.json', 'r') as attendance_file:
        data = json.load(attendance_file)
        record = data["history"][name]
        for attendance in record["attendance"]:
            if (attendance["date"] in dates):
                enter_time = attendance["enter_time"]
                leave_time = attendance["leave_time"]
                a = {
                    'name' : name,
                    'enter_time': data_maker.timeToString(enter_time//60, enter_time%60),
                    'leave_time': data_maker.timeToString(leave_time//60, leave_time%60)                    
                }
                ret[attendance["date"]] = a
    if (len(ret) > 0):
        print(ret)
        return json.dumps(ret)
    else:
        print("Dates are either invalid or no record for requested date")
        return("Dates are either invalid or no record for requested date")                




# a = plt.axes(aspect='equal')
# plt.scatter(test_labels, test_predictions)
# plt.xlabel('True Values [Time Spent]')
# plt.ylabel('Predictions [Time Spent]')
# lims = [0, 600]
# plt.xlim(lims)
# plt.ylim(lims)
# _ = plt.plot(lims, lims)
# plt.show()


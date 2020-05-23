# learned tf with https://www.tensorflow.org/tutorials/keras/regression
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers

#import tensorflow_docs as tfdocs
#import tensorflow_docs.modeling

NEW_FILE = True

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
if NEW_FILE or not os.path.exists('time.data'):
  data_maker.write_to_file()

column_names = ['Name', 'Enter', 'Day', 'Time Spent']
raw_dataset = pd.read_csv('time.data', names=column_names,
                      na_values = "?", comment='\t',
                      sep=" ", skipinitialspace=True)


dataset = raw_dataset.copy()
dataset.isna().sum()
dataset = dataset.dropna()
dataset = pd.get_dummies(dataset, prefix='', prefix_sep='')
train_dataset = dataset.sample(frac=0.8,random_state=0)
test_dataset = dataset.drop(train_dataset.index)

train_stats = train_dataset.describe()
train_stats.pop("Time Spent")
train_stats = train_stats.transpose()

train_labels = train_dataset.pop('Time Spent')
test_labels = test_dataset.pop('Time Spent')

def norm(x):
  return (x - train_stats['mean']) / train_stats['std']
normed_train_data = norm(train_dataset)
normed_test_data = norm(test_dataset)

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

EPOCHS = 150
history = model.fit(
  normed_train_data, train_labels,
  epochs=EPOCHS, validation_split = 0.2, verbose=0,
  callbacks=[EpochDots()])
hist = pd.DataFrame(history.history)
hist['epoch'] = history.epoch
hist.tail()

print()

test_predictions = model.predict(normed_test_data).flatten()


def predict_leave(name, enter, day):
  if day < 0 or day > 6:
    return '{} is not a valid day of the week, please put 0-6'.format(day)
  weekday = ['Sunday', 'Monday', 'Tuesday',
             'Wednesday', 'Thursday', 'Friday', 'Saturday']
  my_dataset = pd.DataFrame(data={'Name': [name],
                                  'Enter': [enter],
                                  'Day': [day]})
  my_dataset = pd.get_dummies(my_dataset, prefix='', prefix_sep='')
  normed_data = norm(my_dataset).fillna(value=0)
  my_prediction = model.predict([normed_data]).flatten()
  leave = [int(x) for x in my_prediction][0] + enter
  return '{} came in at {} on a {} and is predicted to leave at {}'.format(
      name,
      data_maker.timeToString(enter//60, enter%60),
      weekday[day],
      data_maker.timeToString(leave//60, leave%60))


# a = plt.axes(aspect='equal')
# plt.scatter(test_labels, test_predictions)
# plt.xlabel('True Values [Time Spent]')
# plt.ylabel('Predictions [Time Spent]')
# lims = [0, 600]
# plt.xlim(lims)
# plt.ylim(lims)
# _ = plt.plot(lims, lims)
# plt.show()


import os.path
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD , Adam
import tensorflow as tf

import json

class Model(object):
    def __init__(self, learning_rate, state_size, history_size, action_size, model_name="default"):
        self.model_name = model_name
        self.state_size = state_size
        self.history_size = history_size
        self.action_size = action_size

        # Setup keras
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        from keras import backend as K
        K.set_session(sess)

        # Network creation (loading)
        self.model = self._buildmodel(state_size, history_size, action_size)
        if os.path.isfile(model_name + ".h5"):
            self.model.load_weights(model_name + ".h5")
        adam = Adam(lr=learning_rate)
        self.model.compile(loss='mse', optimizer=adam)

    def _buildmodel(self, history_size, state_size, action_size):
        shape = (history_size * state_size,)
        model = Sequential()
        model.add(Dense(30, input_shape=shape))
        model.add(Activation('elu'))
        model.add(Dense(30))
        model.add(Activation('elu'))
        model.add(Dense(action_size))
        return model

    def save(self):
        print("save model")
        self.model.save_weights(self.model_name + ".h5", overwrite=True)
        with open(self.model_name + ".json", "w") as outfile:
            json.dump(self.model.to_json(), outfile)

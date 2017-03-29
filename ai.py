import simulator
import time
import random
import os.path
from collections import deque
import math
import numpy as np
import socket
import threading

import json
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD , Adam
import tensorflow as tf

class AI(object):
    def __init__(self, simulator):
        self.observers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", 25555))
        self.sock.listen(5)
        t = threading.Thread(target=self.accept_observer)
        t.daemon = True
        t.start()
        

        # Setup keras
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        from keras import backend as K
        K.set_session(sess)

        # Parameters
        self.actions = [(1,0), (0,1), (1,1), (-1,-1)]
        self.start_visualization_after = 1000
        self.ai_name = "Alice AI"
        self.simulator = simulator
        self.reset()
        self.dt = 0.1
        self.initial_observe = 1000
        self.replay_mem_size = 30000
        self.replay_memory = deque()
        self.batch_size = 64
        self.epsilon = 0.05
        self.learning_rate = 0.001
        self.momentum = 0.0
        self.l2_decay = 0.01
        self.gamma = 0.7
        self.history_size = 10
        self.history = deque()
        for i in range(self.history_size):
            self.history.append(self.bot.get_measurements())

        # Network creation (loading)
        self.model = self.buildmodel()
        if os.path.isfile("model.h5"):
          self.model.load_weights("model.h5")
        adam = Adam(lr=self.learning_rate)
        self.model.compile(loss='mse',optimizer=adam)

    def buildmodel(self):
        shape = (self.history_size * len(self.bot.get_measurements()),)
        model = Sequential()
        model.add(Dense(30, input_shape=shape))
        model.add(Activation('relu'))
        model.add(Dense(30))
        model.add(Activation('relu'))
        model.add(Dense(len(self.actions)))
        return model

    def pick_action(self, epsilon=0.0):
        a_t = np.zeros([len(self.actions)])
        if random.random() <= epsilon:
            a_t[random.randrange(len(self.actions))] = 1
        else:
            hist = [item for sublist in list(self.history) for item in sublist]
            a_t[np.argmax(self.model.predict(np.array([hist])))] = 1
        return a_t

    def reset(self):
        self.bot = simulator.AlicaBot(1, 1, 0, self.simulator)

    def train(self):
        try:
            t = 0
            last_error = 0
            state1 = self.bot.get_measurements()
            self.history.append(state1)
            if len(self.history) > self.history_size:
                    self.history.popleft()
            print("Start training, stop with CTRL + C")
            while True:
                a_t = self.pick_action(self.epsilon)
                if t <= self.initial_observe:
                    a_t = self.pick_action(1.0)
                v_l, v_r = self.actions[np.argmax(a_t)]
                r = self.bot.move(v_l, v_r, self.dt)

                state2 = self.bot.get_measurements()
                terminal = r < 0

                arr = list(self.history)[1:]
                arr.append(state2)
                
                hist1 = [item for sublist in list(self.history) for item in sublist]
                hist2 = [item for sublist in arr for item in sublist]
                self.replay_memory.append((hist1, a_t, r, hist2, terminal))

                if len(self.replay_memory) > self.replay_mem_size:
                    self.replay_memory.popleft()

                if t > self.initial_observe:
                    minibatch = random.sample(self.replay_memory, self.batch_size)
                    inputs = np.zeros((self.batch_size, self.history_size * len(state1)))
                    targets = np.zeros((inputs.shape[0], len(self.actions)))

                    for i in range(0, len(minibatch)):
                        s_t  = minibatch[i][0]
                        a_t  = minibatch[i][1]
                        r    = minibatch[i][2]
                        s_t1 = minibatch[i][3]
                        terminal = minibatch[i][4]

                        inputs[i:i+1] = s_t
                        targets[i] = self.model.predict(np.array([s_t]))
                        Q_sa = self.model.predict(np.array([s_t1]))
                        idx = np.argmax(a_t)

                        if terminal:
                            targets[i, idx] = r
                        else:
                            targets[i, idx] = r + self.gamma * np.max(Q_sa)


                    self.model.train_on_batch(inputs, targets)

                if r < 0:
                    print("Reset: " + str(t) + ", error free: " + str(t - last_error))
                    self.reset()
                    last_error = t

                state1 = state2
                t = t + 1

                if t % 1000 == 0 and t > self.initial_observe:
                    print("save model")
                    self.model.save_weights("model.h5", overwrite=True)
                    with open("model.json", "w") as outfile:
                        json.dump(self.model.to_json(), outfile)

                if len(self.observers) > 0:
                    robot_x = self.bot.robot.x
                    robot_y = self.bot.robot.y
                    robot_heading = self.bot.robot.heading
                    polygons = []
                    
                    measurements = self.bot.get_measurements()
                    for i in range(len(measurements)):
                        sensor = self.bot.robot.sensors[i]
                        dist = measurements[i]

                        dx_left = math.cos(robot_heading + sensor.heading - sensor.cone_width / 2)
                        dx_right = math.cos(robot_heading + sensor.heading + sensor.cone_width / 2)
            
                        dy_left = math.sin(robot_heading + sensor.heading - sensor.cone_width / 2)
                        dy_right = math.sin(robot_heading + sensor.heading + sensor.cone_width / 2)

                        px = robot_x + math.cos(robot_heading) * sensor.x - math.sin(robot_heading) * sensor.y
                        py = robot_y + math.sin(robot_heading) * sensor.x + math.cos(robot_heading) * sensor.y

                        points = [[px, py],
                                  [(px + dx_left  * dist), (py + dy_left  * dist)],
                                  [(px + dx_right * dist), (py + dy_right * dist)]]
                        polygons.append(points)
                    meta_data = {}
                    meta_data["robot_x"] = robot_x
                    meta_data["robot_y"] = robot_y
                    meta_data["robot_heading"] = robot_heading
                    meta_data["polygons"] = polygons
                    data = json.dumps(meta_data)
                    remove = []
                    for x in self.observers:
                        try:
                          x.send(data + "\n")
                        except:
                          print("observer disconnected")
                          remove.append(x)
                    for x in remove:
                        self.observers.remove(x)
                    time.sleep(self.dt)
                    #self.bot.visualize(self.ai_name, state1, 0.01)
        except KeyboardInterrupt:
            print("User Interrupt: end training.")
            return

    def save(self):
        print("save model")
        self.model.save_weights("model.h5", overwrite=True)
        with open("model.json", "w") as outfile:
            json.dump(self.model.to_json(), outfile)
    
    def accept_observer(self):
        while 1:
            (clientsocket, address) = self.sock.accept()
            self.observers.append(clientsocket)

import socket
import threading
import base64
import cv2
import numpy as np


class Hardware(object):
    def __init__(self, sensors, initial_action, host="alice-bot", port=2323):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.sock.send("ai\n".encode("utf-8"))
        self.fsock = self.sock.makefile()

        self._reward = 0
        self._sensor_state = [0 for i in range(len(sensors))]
        self._x, self._y, self._heading, self._accuracy = 0, 0, 0, 0
        self._image = None
        self._action = initial_action

        t = threading.Thread(target=self.receive_data)
        t.setDaemon(True)
        t.start()

    def receive_data(self):
        while True:
            tags = self.fsock.readline().replace("\n", "").split(" ")
            if tags[0] == "reward":
                self._reward = int(tags[1])
                print(self._reward)
            elif tags[0] == "drive":
                action = []
                for i in range(len(tags) - 1):
                    action.append(float(tags[i + 1]) / 100.0)
                #print(action)
                self._action = action
                print(self._action)
            elif tags[0] == "sense":
                sensor_state = []
                for i in range(len(tags) - 1):
                    sensor_state.append(float(tags[i + 1]))
                self._sensor_state = sensor_state
                print(self._sensor_state)
            elif tags[0] == "pos":
                self._x, self._y, self._heading, self._accuracy = float(tags[1]), float(tags[2]), float(tags[3]), float(tags[4])
            elif tags[0] == "img":  
                tmp = base64.b64decode(tags[1])
                nparr = np.fromstring(tmp, np.uint8)
                self._image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imshow("video_raw", cv2.resize(self._image, (800, 600)))
                cv2.waitKey(1)
            else:
                print("Unknown tag {}".format(tags[0]))

    def stop(self):
        self.fsock.close()
        self.sock.close()

    def reward(self, robot, robot_size, collison_reward, step_reward):
        if self._reward != 0:
            reward = self._reward
            self._reward = 0
            return reward
        return step_reward

    def sense(self, robot):
        return self._sensor_state

    def action(self, act):
        self.sock.send(("drive " + str(int(100.0 * act[0])) + " " + str(int(100.0 * act[1])) + "\n").encode("utf-8"))
        return self._action

    def video(self, robot):
        return self._image

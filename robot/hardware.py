import socket
import threading
import cv2


class Hardware(object):
    def __init__(self, sensors, initial_action, host="localhost", port=2323):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.sock.send("ai\n")
        self.fsock = self.sock.makefile()

        self._reward = 0
        self._sensor_state = [0 for i in range(len(sensors))]
        self._action = initial_action
        self.cam = cv2.VideoCapture(0)

        t = threading.Thread(target=self.receive_data)
        t.setDaemon(True)
        t.start()

    def receive_data(self):
        while True:
            tags = self.fsock.readline().replace("\n", "").split(" ")
            if tags[0] == "reward":
                self._reward = int(tags[1])
                print(self._reward)
            if tags[0] == "drive":
                action = []
                for i in range(len(tags) - 1):
                    action.append(float(tags[i + 1]) / 100.0)
                #print(action)
                self._action = action
                print(self._action)
            if tags[0] == "sense":
                sensor_state = []
                for i in range(len(tags) - 1):
                    sensor_state.append(float(tags[i + 1]))
                self._sensor_state = sensor_state
                print(self._sensor_state)

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
        self.sock.send("drive " + str(int(100.0 * act[0])) + " " + str(int(100.0 * act[1])) + "\n")
        return self._action

    def video(self, robot):
        ret, frame = self.cam.read()
        if not ret:
            return None
        return frame

import socket
import sys


class Play(object):
    def __init__(self, dataset, sensors, initial_action):
        self._reward = 0
        self._sensor_state = [0 for i in range(len(sensors))]
        self._action = initial_action
        self._data = open("data/" + dataset + ".log", "a")

    def _tick(self):
        found_sensor = False
        while not found_sensor:
            line = self._data.readline()
            if self._parse_line(line) == "sense":
                found_sensor = True

    def _parse_line(self, line):
        tags = line.replace("\n", "").split(" ")
        if tags[0] == "reward":
            self._reward = int(tags[1])
        if tags[0] == "drive":
            action = []
            for i in range(len(tags) - 1):
                action.append(float(tags[i + 1]))
            self._action = action
        if tags[0] == "sense":
            sensor_state = []
            for i in range(len(tags) - 1):
                sensor_state.append(float(tags[i + 1]))
            self._sensor_state = sensor_state
        return tags[0]

    def reward(self, robot, robot_size, collison_reward, step_reward):
        if self._reward != 0:
            reward = self._reward
            self._reward = 0
            return reward
        return step_reward

    def sense(self, robot):
        self._tick()
        return self._sensor_state

    def action(self, act):
        return self._action

    def video(self, robot):
        return None


class Record(object):
    def __init__(self, dataset):
        self.sock = socket.socket()
        self.sock.connect(("127.0.0.1", 2323))
        self.sock.send("ai\n")
        self.fsock = self.sock.makefile()
        self.out = open("data/" + dataset + ".log", "a")

    def collect_data(self):
        print("Recording...")
        while True:
            self.out.write(self.fsock.readline())
            self.out.flush()

    def stop(self):
        self.fsock.close()
        self.sock.close()
        self.out.close()


def main():
    collector = Record(sys.argv[1])
    try:
        collector.collect_data()
    except KeyboardInterrupt:
        print("User stopped record.")
    collector.stop()

if __name__ == "__main__":
    main()
import numpy as np
import socket
import time
import cv2
import json
import math
import sys
import threading


class VisualisationProvider(object):
    def __init__(self):
        self.observers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", 25555))
        self.sock.listen(5)
        t = threading.Thread(target=self.accept_observer)
        t.daemon = True
        t.start()

    def accept_observer(self):
        while 1:
            (clientsocket, address) = self.sock.accept()
            self.observers.append(clientsocket)

    def broadcast(self, bot):
        if len(self.observers) > 0:
            robot_x = bot.robot.x
            robot_y = bot.robot.y
            robot_heading = bot.robot.heading
            polygons = []

            measurements = bot.get_measurements()
            for i in range(len(measurements)):
                sensor = bot.robot.sensors[i]
                dist = measurements[i]

                dx_left = math.cos(robot_heading + sensor.heading - sensor.cone_width / 2)
                dx_right = math.cos(robot_heading + sensor.heading + sensor.cone_width / 2)

                dy_left = math.sin(robot_heading + sensor.heading - sensor.cone_width / 2)
                dy_right = math.sin(robot_heading + sensor.heading + sensor.cone_width / 2)

                px = robot_x + math.cos(robot_heading) * sensor.x - math.sin(robot_heading) * sensor.y
                py = robot_y + math.sin(robot_heading) * sensor.x + math.cos(robot_heading) * sensor.y

                points = [[px, py],
                          [(px + dx_left * dist), (py + dy_left * dist)],
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


class NetworkRenderer(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((sys.argv[1], 25555))
        self.fsock = self.sock.makefile()
        self.bg = cv2.imread("../robot/data/map.png")
        if self.bg is None:
            self.bg = cv2.imread("robot/data/map.png")
        self.img = None
        self.scale = 100
        self.height, self.width, self.colors = self.bg.shape
        self.network_read()

    def clear(self):
        self.img = self.bg.copy()

    def draw_line(self, x1, y1, x2, y2, color, width):
        start = (int(x1 * self.scale), int(self.height - y1 * self.scale))
        end = (int(x2 * self.scale), int(self.height - y2 * self.scale))
        cv2.line(self.img, start, end, color, width)

    def draw_circle(self, x, y, radius, color):
        center = (int(x * self.scale), int(self.height - y * self.scale))
        cv2.circle(self.img, center, int(radius * self.scale), color, -1)

    def draw_polygon(self, polygon, color):
        transformed = []
        for p in polygon:
            t = [p[0] * self.scale, self.height - p[1] * self.scale]
            transformed.append(t)
        pts = np.array(transformed, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(self.img, [pts], True, color)

    def network_read(self):
        while True:
            data = json.loads(self.fsock.readline().replace("\n", ""))
            rx = data["robot_x"]
            ry = data["robot_y"]
            rt = data["robot_heading"]
            polygons = data["polygons"]
            self.clear()
            self.draw_circle(rx, ry, 0.15, (50, 0, 200))
            self.draw_line(rx, ry, rx + math.cos(rt), ry + math.sin(rt), (30, 30, 30), 3)
            for poly in polygons:
                self.draw_polygon(poly, (200, 100, 100))
            cv2.imshow("Alice Bot", self.img)
            cv2.waitKey(1)


def main():
    """
    The main function of the program.
    """
    bg = cv2.imread("../robot/data/map.png")
    if bg is None:
        bg = cv2.imread("robot/data/map.png")
    while True:
        try:
            NetworkRenderer()
        except KeyboardInterrupt:
            break
        except:
            time.sleep(1)
            cv2.imshow("Alice Bot", bg)
            cv2.waitKey(1)

if __name__ == "__main__":
    main()

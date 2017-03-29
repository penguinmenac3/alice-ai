import numpy as np
import socket
import threading
import cv2
import json
import math

class NetworkRenderer(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("pm-learn", 25555))
        self.fsock = self.sock.makefile()
        self.bg = cv2.imread("map.png")
        self.img = None
        self.scale = 100
        self.height, self.width, self.colors = self.bg.shape
        self.network_read()

    def clear(self):
        self.img = self.bg.copy()

    def draw_line(self, x1, y1, x2, y2, color, width):
        start = (int(x1 * self.scale), int(self.height - y1 * self.scale))
        end = (int(x2 * self.scale), int(self.height - y2 * self.scale))
        cv2.line(self.img,start,end,color,width)

    def draw_circle(self, x, y, radius, color):
        center = (int(x * self.scale), int(self.height - y * self.scale))
        cv2.circle(self.img, center, int(radius * self.scale), color, -1)

    def draw_polygon(self, polygon, color):
        transformed = []
        for p in polygon:
            t = [p[0] * self.scale, self.height - p[1] * self.scale]
            transformed.append(t)
        pts = np.array(transformed, np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(self.img,[pts],True,color)

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
            cv2.imshow("Alice Bot Learner", self.img)
            cv2.waitKey(1)


NetworkRenderer()

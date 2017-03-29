import numpy as np
from scipy import misc
import math
import random

class Sensor(object):
    def __init__(self, x, y, max_range, cone_width, heading):
        self.x = x
        self.y = y
        self.max_range = max_range
        self.cone_width = cone_width
        self.heading = heading


class Robot(object):
    def __init__(self, x, y, heading, sensors):
        self.x = x
        self.y = y
        self.heading = heading
        self.sensors = sensors


class AlicaBot(object):
    def __init__(self, x, y, heading, simulator):
        sensors = [Sensor(0.12, 0.08, 2, math.radians(30), math.radians(45)),
                   Sensor(0.14, 0.04, 2, math.radians(30), math.radians(15)),
                   Sensor(0.14, -0.04, 2, math.radians(30), math.radians(-15)),
                   Sensor(0.12, -0.08, 2, math.radians(30), math.radians(-45))]#,
                   #Sensor(-0.15, 0, 2, math.radians(30), math.radians(-180))]
        self.robot = Robot(x, y, heading, sensors)
        self.simulator = simulator
        self.wheel_distance = 0.2
        self.size = 0.15

    def get_measurements(self):
        measurements = []
        for i in self.robot.sensors:
            measurements.append(self.simulator.sense_cone(self.robot, i))
        return measurements
        
    def get_state(self):
        return self.get_measurements()

    def move(self, v_left, v_right, dt):
        dx = math.cos(self.robot.heading) / 2.0 * (v_left + v_right)
        dy = math.sin(self.robot.heading) / 2.0 * (v_left + v_right)
        dtheta = -1.0 / self.wheel_distance * v_left + 1.0 / self.wheel_distance * v_right

        self.robot.x += dx * dt
        self.robot.y += dy * dt
        self.robot.heading += dtheta * dt

        while self.robot.heading > math.pi:
            self.robot.heading -= 2 * math.pi
        while self.robot.heading <= -math.pi:
            self.robot.heading += 2 * math.pi

        if self.simulator.collides_circle(self.robot, self.size):
            return -100
        else:
            return 1


class Simulator(object):
    def __init__(self, small=True):
        if small:
            self.simulation_steps_per_meter = 10
            self.map = misc.imread('map_small.png')
            self.pixels_per_meter = 10
            self.simulation_steps_per_radian = 1.0 / math.radians(4)
        else:
            self.simulation_steps_per_meter = 100
            self.map = misc.imread('map.png')
            self.pixels_per_meter = 100
            self.simulation_steps_per_radian = 1.0 / math.radians(9)
        self.map_height, self.map_width, self.colors = self.map.shape

    def collides_circle(self, robot, circle_size):
        x = robot.x
        y = robot.y
        for i in range(int(circle_size * self.pixels_per_meter * 2)):
            for j in range(int(circle_size * self.pixels_per_meter * 2)):
                ioff = i - int(self.pixels_per_meter * circle_size)
                joff = j - int(self.pixels_per_meter * circle_size)
                if ioff * ioff + joff * joff < int(circle_size * self.pixels_per_meter) * int(circle_size * self.pixels_per_meter):
                    ix = int(x * self.pixels_per_meter) + ioff
                    iy = int(y * self.pixels_per_meter) + joff
                    if self.map[self.map_height - iy - 1][ix][0] < 10:
                        return True
        return False

    def sense_cone(self, robot, sensor, relative_angle=0):
        angle_steps = max(1, int(sensor.cone_width * self.simulation_steps_per_radian))
        #print(angle_steps)
        min_val = sensor.max_range

        for alpha in range(angle_steps):
            angle = robot.heading + sensor.heading + relative_angle + (alpha - int(angle_steps / 2.0)) / self.simulation_steps_per_radian
            dx = math.cos(angle)
            dy = math.sin(angle)

            for i in range(sensor.max_range * self.simulation_steps_per_meter):
                dist = i / float(self.simulation_steps_per_meter)
                if dist > min_val:
                    break

                x = robot.x + math.cos(robot.heading) * sensor.x - math.sin(robot.heading) * sensor.y + dx * i / float(self.simulation_steps_per_meter)
                y = robot.y + math.sin(robot.heading) * sensor.x + math.cos(robot.heading) * sensor.y + dy * i / float(self.simulation_steps_per_meter)

                ix = int(x * self.pixels_per_meter)
                iy = int(y * self.pixels_per_meter)
                if 0 <= ix < self.map_width and 0 <= iy < self.map_height:
                    if self.map[self.map_height - iy - 1][ix][0] < 10 and dist < min_val:
                        min_val = dist
                        break

        return 0 if min_val == sensor.max_range else min_val

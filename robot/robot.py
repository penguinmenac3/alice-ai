import math
import simulator
import hardware
import recorder

MAX_SPEED_LEFT = 1
MAX_SPEED_RIGHT = 1.01

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


class AliceBot(object):
    def __init__(self, mode, visualisation):
        sensors = [Sensor(0.12, 0.08, 2, math.radians(30), math.radians(45)),
                   Sensor(0.14, 0.04, 2, math.radians(30), math.radians(15)),
                   Sensor(0.14, -0.04, 2, math.radians(30), math.radians(-15)),
                   Sensor(0.12, -0.08, 2, math.radians(30), math.radians(-45))]  # ,
        # Sensor(-0.15, 0, 2, math.radians(30), math.radians(-180))]
        initial_action = [0, 0]
        self.actions = [(0.5, 0), (0, 0.5), (0.5, 0.5), (-0.3, -0.3)]
        self.action_dimension = 2

        self.state_size = len(sensors)

        self.visualisation = visualisation

        if mode == "simulation":
            x = 1
            y = 1
            heading = 0
            self.environment = simulator.Simulator()

        elif mode == "hardware":
            x = 1
            y = 1
            heading = 0
            self.environment = hardware.Hardware(sensors, initial_action)

        else:
            x = 1
            y = 1
            heading = 0
            self.environment = recorder.Play(mode, sensors, initial_action)
        self.robot = Robot(x, y, heading, sensors)
        self.wheel_distance = 0.2
        self.size = 0.15
        self.mode = mode

    def get_video(self):
        return self.environment.video(self.robot)

    def get_measurements(self):
        return self.environment.sense(self.robot)

    def get_state(self):
        return self.get_measurements()

    def get_pose(self):
        return [self.robot.x, self.robot.y, self.robot.heading]

    def reset(self):
        if self.mode == "simulation":
            self.set_pose(1, 1, 0)

    def set_pose(self, x, y, heading):
        self.robot.x = x
        self.robot.y = y
        self.robot.heading = heading

    def act(self, action, dt=0.1):
        action = self.environment.action(action)
        v_left = MAX_SPEED_LEFT * action[0]
        v_right = MAX_SPEED_RIGHT * action[1]
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

        self.visualisation.broadcast(self)

        return action, self.environment.reward(self.robot, self.size, -100, 1)

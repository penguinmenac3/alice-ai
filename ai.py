import simulator
import time


class AI(object):
    def __init__(self, simulator):
        self.ai_name = "Alice AI"
        self.simulator = simulator
        self.reset()
        self.dt = 0.1

    def pick_action(self, measurements):
        return 0.1, 0.2

    def learn(self, measurements, v_left, v_right, reward):
        pass

    def reset(self):
        self.bot = simulator.AlicaBot(1, 1, 0, self.simulator)

    def train(self):
        try:
            while True:
                measurements = self.bot.get_measurements()
                v_left, v_right = self.pick_action(measurements)
                r = self.bot.move(v_left, v_right, self.dt)
                self.learn(measurements, v_left, v_right, r)

                print("Reward: " + str(r))

                if r < 0:
                    self.reset()

                self.bot.visualize(self.ai_name, measurements, 0.01)
        except KeyboardInterrupt:
            print("User Interrupt: end training.")
            return

    def save(self):
        pass
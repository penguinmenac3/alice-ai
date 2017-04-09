import random
import numpy as np
from collections import deque


class Agent(object):
    def __init__(self, bot, model):
        # Parameters
        self.model = model
        self.bot = bot
        self.history_size = model.history_size
        self.history = deque()
        self.clear_history()

    def clear_history(self):
        self.history = deque()
        for i in range(self.history_size):
            self.history.append(self.bot.get_state())

    def pick_action_one_hot(self, state, epsilon=0.0):
        # Update the history
        self.history.append(state)
        if len(self.history) > self.history_size:
            self.history.popleft()

        # Pick an action using a one hot representation
        a_t = np.zeros([self.model.action_size])
        if random.random() <= epsilon:
            a_t[random.randrange(self.model.action_size)] = 1
        else:
            hist = [item for sublist in list(self.history) for item in sublist]
            a_t[np.argmax(self.model.model.predict(np.array([hist])))] = 1
        return a_t

    def pick_action_regression(self, state, epsilon=0.0):
        # Update the history
        self.history.append(state)
        if len(self.history) > self.history_size:
            self.history.popleft()

        action = None
        if random.random() <= epsilon:
            action = self.bot.actions[random.randrange(len(self.bot.actions))]
        else:
            hist = [item for sublist in list(self.history) for item in sublist]
            action = self.model.model.predict(np.array([hist]))
        return action


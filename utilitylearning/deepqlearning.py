import time
import random
from collections import deque
import numpy as np
import os
import cv2


class Trainer(object):
    def __init__(self, bot, agent, model, memory_name="default"):
        self.bot = bot
        self.agent = agent
        self.model = model

        self.dt = 0.1
        self.initial_observe = 1000
        self.replay_mem_size = 60000
        self.replay_memory = deque()
        self.replay_memory_bad = deque()
        self.batch_size = 64
        self.epsilon = 0.05
        self.momentum = 0.0
        self.l2_decay = 0.01
        self.gamma = 0.7

        self.memory_name = memory_name

        if os.path.isfile(memory_name + ".npz"):
            data = dict(np.load(memory_name + ".npz"))["arr_0"][()]
            self.replay_memory = deque(data["replay_memory"])
            self.replay_memory_bad = deque(data["replay_memory_bad"])
            print()

    def save(self):
        data = {}
        data["replay_memory"] = list(self.replay_memory)
        data["replay_memory_bad"] = list(self.replay_memory_bad)
        np.savez(self.memory_name, data)
        print("Saved trainer memory.")

    def _add_to_replay_memory(self, state, action, reward):
        arr = list(self.agent.history)[1:]
        arr.append(state)
        terminal = reward < 0
        hist1 = [item for sublist in list(self.agent.history) for item in sublist]
        hist2 = [item for sublist in arr for item in sublist]
        if reward >= 0:
            self.replay_memory.append((hist1, action, reward, hist2, terminal))
        else:
            self.replay_memory_bad.append((hist1, action, reward, hist2, terminal))


        if len(self.replay_memory) > self.replay_mem_size:
            self.replay_memory.popleft()
        
        if len(self.replay_memory_bad) > self.replay_mem_size:
            self.replay_memory_bad.popleft()

    def _train_step(self):
        minibatch = random.sample(list(self.replay_memory_bad) + list(self.replay_memory), self.batch_size)
        inputs = np.zeros((self.batch_size, self.model.history_size * self.model.state_size))
        targets = np.zeros((inputs.shape[0], self.model.action_size))

        for i in range(0, len(minibatch)):
            s_t = minibatch[i][0]
            a_t = minibatch[i][1]
            r = minibatch[i][2]
            s_t1 = minibatch[i][3]
            terminal = minibatch[i][4]

            inputs[i:i + 1] = s_t
            targets[i] = self.model.model.predict(np.array([s_t]))
            Q_sa = self.model.model.predict(np.array([s_t1]))
            idx = np.argmax(a_t)

            if terminal:
                targets[i, idx] = r
            else:
                targets[i, idx] = r + self.gamma * np.max(Q_sa)

        self.model.model.train_on_batch(inputs, targets)

    def train(self, plot_error=False):
        stats = []
        if plot_error:
            import matplotlib.pyplot as plt
            plt.ion()
        try:
            t = max(0, len(self.replay_memory))
            last_error = 0
            state = self.bot.get_state()
            img = self.bot.get_video()
            print("Start training, stop with CTRL + C")
            while True:
                timing_start = time.time()

                # Let the agent pick an action.
                action = None
                if t <= self.initial_observe:
                    action = self.agent.pick_action_one_hot(state, 1.0)
                else:
                    action = self.agent.pick_action_one_hot(state, self.epsilon)

                # Execute the action and observe
                act, r = self.bot.act(self.bot.actions[np.argmax(action)], self.dt)
                state = self.bot.get_state()
                img = self.bot.get_video()

                # Create two entries for the replay memory
                self._add_to_replay_memory(state, action, r)

                # Do a training step
                if t > self.initial_observe:
                    self._train_step()

                # Try to reset if we are in a simulation environment
                if r < 0:
                    error_free = t - last_error
                    stats.append(error_free)
                    if plot_error:
                        plt.clf()
                        plt.gcf().canvas.set_window_title("collision free statistic")
                        plt.ylabel("collision free steps")
                        plt.xlabel("collision Id")
                        plt.plot(stats)
                        plt.pause(0.001)
                    print("Reset: " + str(t) + ", error free: " + str(t - last_error))
                    self.agent.clear_history()
                    last_error = t

                # Save the model
                if t % 1000 == 0 and t > self.initial_observe:
                    print("save model")
                    self.model.save()

                elapsed_time = time.time() - timing_start
                sleep_time = max(0, self.dt - elapsed_time)
                time.sleep(sleep_time)
                if plot_error:
                    plt.pause(0.001)
                t += 1
        except KeyboardInterrupt:
            print("User Interrupt: end training.")
            return

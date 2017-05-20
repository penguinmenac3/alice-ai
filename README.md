# alice-ai

Alice Bot AI (with simulator)

__An aiframework for alice-bot.__

By providing a hardware, record/playback and simulated robot interface you can simply experiment with algorithms to learn controling alice-bot.

The repository comes with a simple deep q learner for now.
Reinforce algorithm will be added in the future.

## Some images

![An image of the simulator](https://github.com/penguinmenac3/alice-ai/raw/master/images/Alice-Simulator.png)


![An image of the learning curve](https://github.com/penguinmenac3/alice-ai/raw/master/images/Alice-DeepQLearningCurve.png)

## Installation

TODO

## Usage

```bash
python main.py --help

python visualisation/visualisation.py <host>
```

## Map

The provided map should simulate a small dorm room.

### Normal

1 cm = 1 px

### Small

10cm = 1 px

## Robot data

### Starting position

(x,y) = (1, 1)

### Size

radius = 0.15m


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

### Running the ai.

```bash
python main.py --help
```

### Running the visualisation

If you do not want to run the visualisation on the same machine as the ai using the --visualisation parameter, you can use this tool to connect to any host where the ai is running.

```bash
python visualisation/visualisation.py <host>
```

### Recording data

Record your drives with the real robot to use them for behavioural cloning.

```bash
python robot/recorder.py <dataset> <host>
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


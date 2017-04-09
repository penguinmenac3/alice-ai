from robot.robot import AliceBot
from visualisation.visualisation import VisualisationProvider
from utilitylearning.agent import Agent
from utilitylearning.deepqlearning import Trainer
from utilitylearning.model import Model
import sys


def main():
    """
    The main function of the program.

    Creates an ai and a simulator.
    Trains the ai with the simulator and saves ai state.
    """
    mode = "hardware"
    if (len(sys.argv) > 1):
        mode = sys.argv[1]

    visualisation = VisualisationProvider()
    robot = AliceBot(mode, visualisation)

    model = Model(0.001, robot.state_size, 10, len(robot.actions), model_name="deepqlearning")
    agent = Agent(robot, model)
    trainer = Trainer(robot, agent, model)
    trainer.train(plot_error=True)
    model.save()

if __name__ == "__main__":
    main()

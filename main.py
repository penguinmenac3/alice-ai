import simulator
import agent
import sys


def main():
    """
    The main function of the program.

    Creates an ai and a simulator.
    Trains the ai with the simulator and saves ai state.
    """
    small = False
    if (len(sys.argv) > 1) and sys.argv[1] == "small":
        small = True
    my_simulator = simulator.Simulator(small)
    my_agent = agent.Agent(my_simulator)
    my_agent.train()
    my_agent.save()

if __name__ == "__main__":
    main()

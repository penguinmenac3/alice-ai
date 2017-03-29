import simulator
import ai
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
    my_ai = ai.AI(my_simulator)
    my_ai.train()
    my_ai.save()

if __name__ == "__main__":
    main()

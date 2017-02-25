import simulator
import ai


def main():
    """
    The main function of the program.

    Creates an ai and a simulator.
    Trains the ai with the simulator and saves ai state.
    """
    my_simulator = simulator.Simulator()
    my_ai = ai.AI(my_simulator)
    my_ai.train()
    my_ai.save()

if __name__ == "__main__":
    main()

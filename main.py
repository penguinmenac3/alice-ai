import sys, subprocess

def show_help(): 
    print("usage: python main.py [OPTION]")
    print("")
    print("Options and Arguments:")
    print("  -s, --simulation, --simulator    Use a simulation instead of the hardware robot.")
    print("  -e, --plot_error                 Plot the error as a matplotlib chart.")
    print("  -h, --help                       Show this help.")
    print("  -v, --visualization              Open a visualisation.")

def main():
    """
    The main function of the program.

    Creates an ai and a simulator.
    Trains the ai with the simulator and saves ai state.
    """
    mode = "--hardware"
    plot_error = False
    proc = None
    for i in range(len(sys.argv) - 1):
        arg = sys.argv[i + 1]
        if arg == "--help" or arg == "-h":
            show_help()
            return
        elif arg == "-s" or arg == "--simulation" or arg == "--simulator":
            mode = "simulation"
        elif arg == "--hardware":
            mode = "hardware"
        elif arg == "-e" or arg == "--plot_error":
            plot_error = True
        elif arg == "-v" or arg == "--visualization":
            proc = subprocess.Popen(["python", "visualisation/visualisation.py", "localhost"])
        else:
            print("Unknown option: " + arg)
            show_help()
            return

    from robot.robot import AliceBot
    from visualisation.visualisation import VisualisationProvider
    from utilitylearning.agent import Agent
    from utilitylearning.deepqlearning import Trainer
    from utilitylearning.model import Model

    visualisation = VisualisationProvider()
    robot = AliceBot(mode, visualisation)

    model = Model(0.001, robot.state_size, 10, len(robot.actions), model_name="deepqlearning")
    agent = Agent(robot, model)
    trainer = Trainer(robot, agent, model)
    trainer.train(plot_error=plot_error)
    model.save()
    if proc is not None:
        proc.kill()

if __name__ == "__main__":
    main()

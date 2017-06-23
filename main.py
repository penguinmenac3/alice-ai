import sys, subprocess

def show_help(): 
    print("usage: python main.py [OPTION]")
    print("")
    print("Options and Arguments:")
    print("      --playback=dataset           Playback a record to the ai.")
    print("  -e, --plot_error                 Plot the error as a matplotlib chart.")
    print("  -h, --help                       Show this help.")
    print("  -v, --visualization              Open a visualisation.")

def main():
    """
    The main function of the program.

    Creates an ai and a simulator.
    Trains the ai with the simulator and saves ai state.
    """
    mode = "hardware"
    plot_error = False
    proc = None
    for i in range(len(sys.argv) - 1):
        arg = sys.argv[i + 1]
        if arg == "--help" or arg == "-h":
            show_help()
            return
        elif arg == "--hardware":
            mode = "hardware"
        elif arg.split("=")[0] == "--playback":
            mode = arg.split("=")[1]
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
    trainer = Trainer(robot, agent, model, memory_name="deepqlearning")
    trainer.train(plot_error=plot_error)
    trainer.save()
    model.save()
    if proc is not None:
        proc.kill()

if __name__ == "__main__":
    main()

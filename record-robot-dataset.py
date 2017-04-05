import numpy as np
import socket

class DatasetCollector(object):
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect(("127.0.0.1", 2323))
        self.fsock = self.sock.makefile()
        self.out = open("robot.log", "a")

    def collect_data(self):
        while True:
            self.out.write(self.fsock.readline())
            self.out.flush()

    def stop(self):
        self.fsock.close()
        self.sock.close()
        self.out.close()

def main():
    collector = DatasetCollector()
    try:
        collector.collect_data()
    except KeyboardInterrupt:
        print("User stopped record.")
    collector.stop()

if __name__ == "__main__":
    main()

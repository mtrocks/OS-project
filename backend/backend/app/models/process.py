class Process:
    def __init__(self, pid, arrival=0, burst=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst

        self.remaining = burst

        self.completion = 0
        self.tat = 0
        self.wt = 0
        self.rt = -1
        self.done = False
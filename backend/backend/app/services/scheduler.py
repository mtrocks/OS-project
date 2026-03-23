from app.algorithms.fcfs import fcfs
from app.algorithms.sjf import sjf
from app.algorithms.ljf import ljf
from app.algorithms.rr import round_robin

def run_algorithm(algo, processes, tq=None):

    if algo == "fcfs":
        return fcfs(processes)

    if algo == "sjf":
        return sjf(processes)

    if algo == "ljf":
        return ljf(processes)

    if algo == "rr":
        return round_robin(processes, tq)
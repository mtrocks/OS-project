from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.models.process import Process
from app.services.scheduler import run_algorithm

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessInput(BaseModel):
    pid: str
    arrival: int = 0
    burst: int

class ScheduleRequest(BaseModel):
    algorithm: str
    time_quantum: int | None = None
    processes: List[ProcessInput]

@app.get("/test")
def test_connection():
    return {"message": "The backend is alive and reachable!"}


@app.post("/schedule")
def schedule(data: ScheduleRequest):
    
    # Helper function to generate fresh process objects for every simulation run.
    def get_fresh_processes():
        return [Process(p.pid, p.arrival, p.burst) for p in data.processes]

    # 1. Run the primary algorithm selected by the user for the main tables and Gantt chart
    output = run_algorithm(
        data.algorithm,
        get_fresh_processes(),
        data.time_quantum
    )

    # 2. Run all algorithms to gather data for the comparison chart
    # We provide a default of 2 if one isn't present in the request.
    tq_for_comparison = data.time_quantum if data.time_quantum else 2
    
    algorithms = {
        "fcfs": "FCFS",
        "sjf": "SJF",
        "ljf": "LJF",
        "rr": "Round Robin"
    }

    comparison_data = []

    for algo_key, algo_name in algorithms.items():
        try:
            res = run_algorithm(algo_key, get_fresh_processes(), tq_for_comparison)
            metrics = res.get("metrics", {})

            comparison_data.append({
                "name": algo_name,
                "avgTAT": metrics.get("avg_tat", 0),
                "avgWT": metrics.get("avg_wt", 0),
                "avgRT": metrics.get("avg_rt", 0),
                "cpuUtil": metrics.get("cpu_util", 0),
                "throughput": metrics.get("throughput", 0)
            })
        except Exception as e:
            print(f"Failed to generate comparison for {algo_key}: {e}")

    output["comparison"] = comparison_data

    return output
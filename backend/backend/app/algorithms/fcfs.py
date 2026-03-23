from copy import deepcopy

def fcfs(processes):
    # Deepcopy ensures we don't accidentally modify the original input data
    processes = deepcopy(processes)
    
    processes.sort(key=lambda x: x.arrival)

    current_time = 0
    gantt = []
    result = []

    total_tat = total_wt = total_rt = total_burst = 0

    for p in processes:
        # If the CPU is ready before the next process arrives, the CPU is IDLE
        if current_time < p.arrival:
            gantt.append({
                "pid": "Idle", 
                "start": current_time, 
                "end": p.arrival
            })
            current_time = p.arrival

        start = current_time
        completion = start + p.burst
        
        # Calculate standard OS metrics
        tat = completion - p.arrival
        wt = tat - p.burst
        rt = start - p.arrival  

        # Record for visualization
        gantt.append({
            "pid": p.pid,
            "start": start,
            "end": completion
        })

        # Record for the final results table
        result.append({
            "pid": p.pid,
            "arrival": p.arrival,
            "burst": p.burst,
            "completion": completion,
            "tat": tat,
            "wt": wt,
            "rt": rt
        })

        current_time = completion

        total_tat += tat
        total_wt += wt
        total_rt += rt
        total_burst += p.burst

    n = len(processes)
    total_time = current_time - min(p.arrival for p in processes)

    metrics = {
        "avg_tat": round(total_tat / n, 2) if n > 0 else 0,
        "avg_wt": round(total_wt / n, 2) if n > 0 else 0,
        "avg_rt": round(total_rt / n, 2) if n > 0 else 0,
        "throughput": round(n / total_time, 4) if total_time > 0 else 0,
        "cpu_util": round((total_burst / total_time) * 100, 2) if total_time > 0 else 0,
        "total_time": total_time
    }

    return {"processes": result, "gantt": gantt, "metrics": metrics}
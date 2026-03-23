from copy import deepcopy

def ljf(processes):
    processes = deepcopy(processes)
    n = len(processes)
    
    completed = 0
    current_time = 0

    gantt = []
    result = []

    total_tat = total_wt = total_rt = total_burst = 0

    # Keep running until all processes are finished
    while completed < n:

        available = [p for p in processes if p.arrival <= current_time and not p.done]

        # If no processes have arrived yet, the CPU sits idle
        if not available:
            # Find the time the next process arrives to jump forward
            next_arrival = min([p.arrival for p in processes if not p.done])
            gantt.append({
                "pid": "Idle", 
                "start": current_time, 
                "end": next_arrival
            })
            current_time = next_arrival
            continue

        # LJF Logic: Pick the available process with the HIGHEST burst time
        current = max(available, key=lambda x: x.burst)
        
        # Mark as done so we don't pick it again
        current.done = True

        start = current_time
        completion = start + current.burst
        
        tat = completion - current.arrival
        wt = tat - current.burst
        rt = start - current.arrival

        gantt.append({"pid": current.pid, "start": start, "end": completion})

        result.append({
            "pid": current.pid,
            "arrival": current.arrival,
            "burst": current.burst,
            "completion": completion,
            "tat": tat,
            "wt": wt,
            "rt": rt
        })

        # Move the clock forward
        current_time = completion
        completed += 1

        total_tat += tat
        total_wt += wt
        total_rt += rt
        total_burst += current.burst

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
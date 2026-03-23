from copy import deepcopy

def sjf(processes):
    processes = deepcopy(processes)

    n = len(processes)
    completed = 0
    current_time = 0

    gantt = []
    result = []

    total_tat = total_wt = total_rt = total_burst = 0

    while completed < n:

        available = [p for p in processes if p.arrival <= current_time and not p.done]
        if not available:
            current_time += 1
            continue

        current = min(available, key=lambda x: x.burst)
        current.done = True

        start = max(current_time, current.arrival)

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

        current_time = completion
        completed += 1

        total_tat += tat
        total_wt += wt
        total_rt += rt
        total_burst += current.burst

    total_time = current_time - min(p.arrival for p in processes)

    metrics = {
        "avg_tat": total_tat / n,
        "avg_wt": total_wt / n,
        "avg_rt": total_rt / n,
        "throughput": n / total_time,
        "cpu_util": (total_burst / total_time) * 100,
        "total_time": total_time
    }

    return {"processes": result, "gantt": gantt, "metrics": metrics}
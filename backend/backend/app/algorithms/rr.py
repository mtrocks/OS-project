from collections import deque
from copy import deepcopy

def round_robin(processes, time_quantum):
    # Deepcopy to avoid modifying original objects if used elsewhere
    proc_list = deepcopy(processes)
    # Sort by arrival time
    proc_list.sort(key=lambda x: x.arrival)

    n = len(proc_list)
    remaining_burst = {p.pid: p.burst for p in proc_list}
    completion_time = {}
    response_time = {p.pid: -1 for p in proc_list}
    
    # Ready queue stores PIDs
    ready_queue = deque()
    
    current_time = 0
    completed = 0
    
    # To track who is in queue
    in_queue = {p.pid: False for p in proc_list}
    
    # Push initial processes
    # We must push ALL processes that have arrived at time 0
    for p in proc_list:
        if p.arrival <= current_time and not in_queue[p.pid]:
            ready_queue.append(p.pid)
            in_queue[p.pid] = True

    gantt = []
    
    # Main Loop
    while completed < n:
        if not ready_queue:
            # CPU Idle logic
            # Find the next arriving process
            next_arrival = float('inf')
            for p in proc_list:
                if remaining_burst[p.pid] > 0 and p.arrival < next_arrival:
                    next_arrival = p.arrival
            
            if next_arrival == float('inf'): break # Should not happen if completed < n

            # Add idle block to gantt
            gantt.append({"pid": "Idle", "start": current_time, "end": next_arrival})
            current_time = next_arrival
            
            # Add newly arrived processes
            for p in proc_list:
                if p.arrival <= current_time and remaining_burst[p.pid] > 0 and not in_queue[p.pid]:
                    ready_queue.append(p.pid)
                    in_queue[p.pid] = True
            continue

        pid = ready_queue.popleft()
        in_queue[pid] = False # It's out of queue, executing
        
        # Find the actual process object
        p = next(x for x in proc_list if x.pid == pid)

        # Record Response Time (First time getting CPU)
        if response_time[pid] == -1:
            response_time[pid] = current_time - p.arrival

        # Execute
        exec_time = min(time_quantum, remaining_burst[pid])
        start_time = current_time
        current_time += exec_time
        remaining_burst[pid] -= exec_time
        
        gantt.append({"pid": pid, "start": start_time, "end": current_time})

        # Check for new arrivals DURING execution
        for proc in proc_list:
            if (proc.pid != pid and 
                proc.arrival <= current_time and 
                remaining_burst[proc.pid] > 0 and 
                not in_queue[proc.pid]):
                ready_queue.append(proc.pid)
                in_queue[proc.pid] = True

        # If process still has burst, put back in queue
        if remaining_burst[pid] > 0:
            ready_queue.append(pid)
            in_queue[pid] = True
        else:
            # Process Finished
            completed += 1
            completion_time[pid] = current_time
            p.completion = current_time
            p.tat = p.completion - p.arrival
            p.wt = p.tat - p.burst
            p.rt = response_time[pid]

    # Prepare Result List
    result = []
    total_tat = total_wt = total_rt = total_burst = 0
    
    for p in proc_list:
        total_tat += p.tat
        total_wt += p.wt
        total_rt += p.rt
        total_burst += p.burst
        
        result.append({
            "pid": p.pid,
            "arrival": p.arrival,
            "burst": p.burst,
            "completion": p.completion,
            "tat": p.tat,
            "wt": p.wt,
            "rt": p.rt
        })

    # Metrics
    total_time = current_time - min(x.arrival for x in processes)
    metrics = {
        "avg_tat": round(total_tat / n, 2),
        "avg_wt": round(total_wt / n, 2),
        "avg_rt": round(total_rt / n, 2),
        "throughput": round(n / total_time, 4) if total_time > 0 else 0,
        "cpu_util": round((total_burst / total_time) * 100, 2) if total_time > 0 else 0,
        "total_time": total_time
    }

    return {"processes": result, "gantt": gantt, "metrics": metrics}
def calculate_metrics(processes, total_time):
    n = len(processes)
    
    if n == 0 or total_time == 0:
        return {
            "total_time": 0, "avg_tat": 0, "avg_wt": 0, 
            "avg_rt": 0, "throughput": 0, "cpu_util": 0
        }
    # Accessing data
    total_TAT = sum(p["tat"] for p in processes)
    total_WT = sum(p["wt"] for p in processes)
    total_RT = sum(p["rt"] for p in processes)
    total_burst = sum(p["burst"] for p in processes)

    return {
        "total_time": total_time,
        "avg_tat": round(total_TAT / n, 2),
        "avg_wt": round(total_WT / n, 2),
        "avg_rt": round(total_RT / n, 2),
        "throughput": round(n / total_time, 4),
        "cpu_util": round((total_burst / total_time) * 100, 2)
    }
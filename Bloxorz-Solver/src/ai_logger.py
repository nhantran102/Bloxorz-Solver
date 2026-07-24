
import time
import os
import json
import tracemalloc

class AILogger:
    """
    Helper class to log performance metrics for AI algorithms.
    Metrics: Search Time, Memory Usage (Peak), Nodes Expanded, Solution Length.
    """
    def __init__(self, log_file="ai_performance_log.json"):
        self.log_file = log_file

    def log_result(self, level, algorithm, time_taken, memory_usage, nodes_expanded, solution_length):
        data = {
            "level": level,
            "algorithm": algorithm,
            "time_seconds": round(time_taken, 4),
            "peak_memory_mb": round(memory_usage / 10**6, 4),
            "nodes_expanded": nodes_expanded,
            "solution_length": solution_length
        }
        
        # Load existing log or create new list
        logs = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(data)
        
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=4)

# Example of how to integrate into the BloxorzApp class:
# 1. Initialize logger in __init__: self.logger = AILogger()
# 2. In run_solver:
#    tracemalloc.start()
#    start_time = time.time()
#    # ... run algorithm ...
#    path = algorithm(self.game)
#    # ... get stats ...
#    current, peak = tracemalloc.get_traced_memory()
#    tracemalloc.stop()
#    self.logger.log_result(self.level_index, algo_name, time.time() - start_time, peak, len(self.game.visited_nodes), len(path))

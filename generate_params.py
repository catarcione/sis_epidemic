# generate_params.py
import itertools

asymp_rates = [0.01, 0.05, 0.1]
snaps_intervals = [1, 2, 4, 8, 16]
graph_types = ['ba', 'ws', 'er']
n_runs = 30

with open("params.txt", "w") as f:
    for asymp_rate, snaps_interval, gtype in itertools.product(asymp_rates, snaps_intervals, graph_types):
        for run_id in range(n_runs):
            line = f"--asymptomatic_rate {asymp_rate} --snapshots_interval {snaps_interval} --graph_type {gtype} --run_id {run_id}\n"
            f.write(line)
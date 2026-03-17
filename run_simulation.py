# Run simulation
import argparse
import json
import os
import random
import networkx as nx
import numpy as np

import epidemic
import metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asymptomatic_rate", type=float, required=True)
    parser.add_argument("--snapshots_interval", type=int, required=True)
    parser.add_argument("--run_id", type=int, required=True)
    parser.add_argument("--beta", type=float, default=0.01)
    parser.add_argument("--gamma", type=float, default=0.01)
    parser.add_argument("--initial_infected_count", type=int, default=50)
    parser.add_argument("--num_snapshots", type=int, default=10)
    parser.add_argument("--burn_in_steps", type=int, default=1000)
    parser.add_argument("--graph_type", type=str, default="ba")
    parser.add_argument("--n_nodes", type=int, default=3000)
    parser.add_argument("--m_param", type=int, default=4)
    parser.add_argument("--k_param", type=int, default=8, help="WS: Each node is joined with its k nearest neighbors")
    parser.add_argument("--p_rewire", type=float, default=0.3, help="WS: Rewiring probability")
    parser.add_argument("--p_er", type=float, default=8/3000, help="ER: Probability for edge creation")

    parser.add_argument("--output_dir", type=str, default="results")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Generate reproducible seed
    seed = random.randint(0, 2**32 - 1)
    random.seed(seed)
    np.random.seed(seed)

    # Generate graph
    if args.graph_type == "ba":
        graph = nx.barabasi_albert_graph(args.n_nodes, args.m_param, seed=seed)
    elif args.graph_type == "ws":
        graph = nx.watts_strogatz_graph(args.n_nodes, args.k_param, args.p_rewire, seed=seed)
    elif args.graph_type == "er":
        graph = nx.erdos_renyi_graph(args.n_nodes, args.p_er, seed=seed)
    else:
        raise ValueError(f"Unsupported graph type: {args.graph_type}")
    
    asymptomatic = epidemic.choose_asymptomatic_nodes(graph, fraction = args.asymptomatic_rate)
    infected = epidemic.burn_in(graph, args.beta, args.gamma, args.initial_infected_count, args.burn_in_steps)

    snapshots = epidemic.collect_snapshots(graph, args.beta, args.gamma, infected, args.num_snapshots, args.snapshots_interval)

    observed_betws = {}
    contacts = {}
    observations = {}

    for t, I_t in enumerate(snapshots):
        O_t = I_t - asymptomatic
        obs_betw = metrics.observed_betweenness(graph, O_t)
        observed_betws[t] = obs_betw
        # cont = metrics.contact(graph, O_t)
        # contacts[t] = cont
        if t > 0:
            O_t = O_t | observations[t-1]
        observations[t] = O_t
        cont = metrics.contact(graph, O_t)
        contacts[t] = cont

    bound_fprs = {}
    obs_betw_fprs = {}
    contact_fprs = {}

    num_asymp = len(asymptomatic)
    fracs = [0.1, 0.2, 0.5, 0.75, 1]
    top_ks = [int(x * num_asymp) for x in fracs]

    for t, I_t in enumerate(snapshots):
        obs = observations[t]

        betw = metrics.sum_first_t(observed_betws, t)
        conts = contacts[t]
        candidates = [node for node in betw if node not in obs]
        betw_eval = {}
        cont_eval = {}
        for i in candidates:
            betw_eval[i] = betw[i]
            cont_eval[i] = conts[i]
        betw_rank = dict(sorted(betw_eval.items(), key=lambda item: item[1], reverse=True))
        cont_rank = dict(sorted(cont_eval.items(), key=lambda item: item[1], reverse=True))


        betw_results = {}
        cont_results = {}

        for frac, k in zip(fracs, top_ks):
            betw_top = list(betw_rank.keys())[:k]
            cont_top = list(cont_rank.keys())[:k]

            obs_betw_fpr = len(set(betw_top) - asymptomatic) / k
            cont_fpr = len(set(cont_top) - asymptomatic) / k

            betw_results["top-" + str(frac)] = obs_betw_fpr
            cont_results["top-" + str(frac)] = cont_fpr

        bound_fpr = len((graph.nodes() - obs) - asymptomatic)  / len(graph.nodes() - obs)

        bound_fprs[str(t+1)+" snapshots"] = bound_fpr
        obs_betw_fprs[str(t+1)+" snapshots"] = betw_results
        contact_fprs[str(t+1)+" snapshots"] = cont_results

    data = {
        "seed": seed,
        "run_id": args.run_id,
        "graph_type": args.graph_type,
        "asymptomatic_rate": args.asymptomatic_rate,
        "num_snapshots": args.num_snapshots,
        "snapshots_interval": args.snapshots_interval,
        "bound_fprs": bound_fprs,
        "obs_betw_fprs": obs_betw_fprs,
        "cont_fprs": contact_fprs
    }

    filename = f"graph_{args.graph_type}_asymp_rate_{args.asymptomatic_rate}_snaps_interval_{args.snapshots_interval}_run{args.run_id}.json"

    filepath = os.path.join(args.output_dir, filename)

    with open(filepath, "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    main()

# SIS + asymptomatic
import random

def choose_asymptomatic_nodes(graph, fraction, seed=None):
    random.seed(seed)
    nodes = list(graph.nodes())
    k = int(len(nodes) * fraction)
    return set(random.sample(nodes, k))


def epidemic_step(graph, beta, gamma, infected):

    new_infected = set()
    recovered = set()

    for node in infected:
        for neighbor in set(graph.neighbors(node)) - infected:
            if random.random() < beta:
                new_infected.add(neighbor)

    for node in infected:
        if random.random() < gamma:
            recovered.add(node)

    infected = infected | new_infected
    infected = infected - recovered

    return infected


def burn_in(graph, beta, gamma, initial_infected_count, burn_in_steps):
    initial_infected = random.sample(list(graph.nodes()), k=initial_infected_count) # Randomly select the initial infected nodes from the graph
    infected = set(initial_infected)

    for _ in range(burn_in_steps):
        infected = epidemic_step(graph, beta, gamma, infected)
    
    return infected


def collect_snapshots(graph, beta, gamma, infected, num_snapshots, step_between):
    snapshots = []

    for _ in range(num_snapshots):

        for _ in range(step_between):
            infected = epidemic_step(graph, beta, gamma, infected)

        snapshots.append(set(infected))

    return snapshots
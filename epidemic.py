# SIS + Observed betweenness
import random

def epidemic_step(graph, beta, gamma, infected):

    new_infected = set()
    recovered = ()

    infected_list = list(infected)
    random.shuffle(infected_list)

    for node in infected_list:
        for neighbor in set(graph.neighbors(node)) - infected:
            if random.random() < beta:
                new_infected.add(neighbor)

    for node in infected_list:
        if random.random() < gamma:
            recovered.add(node)

    infected = infected | new_infected
    infected = infected - recovered


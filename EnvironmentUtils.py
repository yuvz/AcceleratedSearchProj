import random
from sys import maxsize
from Environment import Agent, AStar


def generate_rand_agents_and_dest_ids(warehouse, waves_per_warehouse):
    sources = warehouse.sources
    num_of_sources = len(sources)
    num_of_waves = waves_per_warehouse[warehouse.warehouse_id - 1]
    agents = []
    dest_ids = []
    for i in range(num_of_waves):
        destinations = random.choices(warehouse.destinations, k=num_of_sources)
        for j in range(num_of_sources):
            agents.append(Agent(i * num_of_sources + j, sources[j], destinations[j]))
            dest_ids.append(destinations[j].destination_id)
    return agents, dest_ids


def get_agent_and_framework(agents, i):
    agent = agents[i]
    agent_vertex = agent.vertex
    source_node = AStar.Node(agent_vertex, agent_vertex.destination_distance[agent.destination.destination_id], 0,
                             None, True)
    destination_node = AStar.Node(agent.destination, 0, maxsize, None, False)
    a_star_framework = AStar(source_node, destination_node)
    return agent, a_star_framework

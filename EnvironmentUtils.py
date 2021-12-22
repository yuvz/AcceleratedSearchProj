import random
from sys import maxsize
from AStar import AStar
from Agent import Agent


def generate_rand_agents(warehouse, waves_per_warehouse):
    sources = warehouse.sources
    num_of_sources = len(sources)
    num_of_waves = waves_per_warehouse[warehouse.warehouse_id - 1]
    agents = []
    for i in range(num_of_waves):
        destinations = random.choices(warehouse.destinations, k=num_of_sources)
        for j in range(num_of_sources):
            agents.append(Agent(i * num_of_sources + j, sources[j], destinations[j]))
    return agents


def find_route_using_Astar(warehouse, plan, agent, is_first_agent=False, wait_at_source_left=0):
    agent_vertex = agent.source
    source_node = AStar.Node(agent_vertex, agent_vertex.destination_distance[agent.destination.destination_id], 0,
                             None, True)
    destination_node = AStar.Node(agent.destination, 0, maxsize, None, False)
    a_star_framework = AStar(source_node, destination_node)
    route = a_star_framework.space_time_search(warehouse, agent, plan, is_first_agent, wait_at_source_left)
    return route


def order_agents_by_key(agents, value_function):
    sorted_agents = sorted(agents, key=value_function)
    sorted_agent_ids = [agent.agent_id for agent in sorted_agents]

    return sorted_agent_ids


def order_agents_by_destination_id(agents):
    return order_agents_by_key(agents, Agent.get_destination_id)


def order_agents_by_source_id(agents):
    return order_agents_by_key(agents, Agent.get_source_id)


def order_agents_by_source_then_destination_id(agents):
    sorted_agents = sorted(agents, key=Agent.get_destination_id)
    sorted_agents = sorted(sorted_agents, key=Agent.get_source_id)

    sorted_agent_ids = [agent.agent_id for agent in sorted_agents]
    return sorted_agent_ids

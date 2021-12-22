from math import sqrt

from Environment import Agent


def distance(u, v):
    return sqrt((u[0] - v[0]) ** 2 + (u[1] - v[1]) ** 2)


def update_plan(plan, i, route):
    if not route:
        return
    for step in route:
        plan[i].append(step)


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

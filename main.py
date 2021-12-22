
import random
import heapq
from sys import maxsize
from colorsys import hls_to_rgb
from matplotlib.animation import FuncAnimation

from copy import deepcopy
from math import ceil, sqrt, floor
from time import time
from Definitions import *
from typing import List, Set, Tuple
from Utils import *

EXPORT_ANIMATION = False
SHOW_ANIMATION_TRAIL = False

RANDOM_SCHEDULING_ENABLED = False

WAVES_PER_WAREHOUSE = [10, 20, 10, 1]
WAREHOUSE_FPS = [24, 3, 6, 12]

PROGRESSIVELY_OBSTACLE_RESTRICTED_PLANS_MAX_TRIES = 5
RANDOM_MIDPOINTS_MAX_TRIES = 5
LNS_ITERATIONS = 1

def generate_warehouse(warehouse_id):
    # First warehouse in original paper
    if warehouse_id == 1:
        length = 100
        width = 150
        number_of_sources = 14
        number_of_destinations = 9
        obstacle_length = round(0.1 * length)
        obstacle_width = round(0.1 * width)

        return Warehouse(warehouse_id, length, width, number_of_sources, number_of_destinations, obstacle_length,
                         obstacle_width)

    # Toy warehouse
    if warehouse_id == 2:
        length = 10
        width = 10
        number_of_sources = 3
        number_of_destinations = 2
        obstacle_length = round(0.1 * length)
        obstacle_width = round(0.1 * width)

        return Warehouse(warehouse_id, length, width, number_of_sources, number_of_destinations, obstacle_length,
                         obstacle_width)

    # small warehouse
    if warehouse_id == 3:
        length = 40
        width = 40
        number_of_sources = 7
        number_of_destinations = 7
        obstacle_length = round(0.1 * length)
        obstacle_width = round(0.1 * width)

        return Warehouse(warehouse_id, length, width, number_of_sources, number_of_destinations, obstacle_length,
                         obstacle_width)

    # mid warehouse
    if warehouse_id == 4:
        length = 40
        width = 40
        number_of_sources = 9
        number_of_destinations = 1
        obstacle_length = round(0.1 * length)
        obstacle_width = round(0.1 * width)

        return Warehouse(warehouse_id, length, width, number_of_sources, number_of_destinations, obstacle_length,
                         obstacle_width)


def plan_to_frames(plan):
    frames = []
    plan_copy = deepcopy(plan)
    appended = True

    while appended:
        appended = False
        frame = []
        for i in range(len(plan_copy)):
            if plan_copy[i]:
                frame.append(plan_copy[i].pop(0))
                appended = True
            else:
                frame.append([])

        if appended:
            frames.append(frame)

    return frames


def agent_plan_to_frames(agent_plan):
    return [[step] for step in agent_plan]


def random_color():
    return hls_to_rgb(random.random(), 0.25 + random.random() / 2.0, 0.25 + random.random() * (3.0 / 4.0))


def show_routes(warehouse, plan, running_time=-1.0, algorithm_name="TODO", dest_ids=None, title=""):
    fig, ax = warehouse.plot_layout()

    # colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), 'xkcd:dark pastel green', 'xkcd:strong pink', '#6dedfd', (1, 0.5, 0.25),
    #           'xkcd:light navy blue', (0.5, 0.25, 1)]
    # if warehouse.warehouse_id == 1:
    #     agent_routes = []
    #     for dest_id in dest_ids:
    #         # if dest_id > 2:
    #         #     continue
    #         agent_routes.append(plt.plot([], [], 'ro', c=colors[dest_id])[0])
    # else:
    #     agent_routes = []
    #     for i in range(len(plan)):
    #         if i == 20:
    #             agent_routes.append(plt.plot([], [], 'ro', c=colors[1])[0])
    #         else:
    #             agent_routes.append(plt.plot([], [], 'ro', c=colors[0])[0])

    agent_routes = [plt.plot([], [], 'ro', c=random_color())[0] for _ in range(len(plan))]
    frames = plan_to_frames(plan)
    xdata = [[] for _ in range(len(plan))]
    ydata = [[] for _ in range(len(plan))]

    def init():
        for agent_route in agent_routes:
            agent_route.set_data([], [])
        return agent_routes

    def animate(frame):
        for i, agent_route in enumerate(agent_routes):
            if frame[i]:
                if SHOW_ANIMATION_TRAIL:
                    if frame == frames[0]:
                        xdata[i] = [frame[i][1]]
                        ydata[i] = [frame[i][0]]
                    else:
                        xdata[i].append(frame[i][1])
                        ydata[i].append(frame[i][0])
                else:
                    agent_route.set_data([frame[i][1], frame[i][0]])

        if SHOW_ANIMATION_TRAIL:
            for i, agent_route in enumerate(agent_routes):
                agent_route.set_data(xdata[i], ydata[i])
        return agent_routes

    t0 = time()
    animate(frames[0])
    t1 = time()
    fps = WAREHOUSE_FPS[warehouse.warehouse_id - 1]
    dt = 1. / fps

    interval = 1000 * dt - (t1 - t0)
    animation = FuncAnimation(fig, animate, frames=frames, init_func=init, blit=True, interval=interval)

    sum_of_costs = sum([len(route) for route in plan])

    title_left = "map_size = " + str(warehouse.width) + "*" + str(warehouse.length) + \
                 "        (num_sources, num_destinations) = " + \
                 str((warehouse.number_of_sources, warehouse.number_of_destinations)) + \
                 "        num_agents = " + str(len(plan)) + \
                 "\nAlgorithm = " + algorithm_name + "        sum_of_costs = " + str(sum_of_costs) + \
                 "        running_time = " + str(running_time)

    plt.title(title_left, loc='left')
    plt.suptitle(title)
    plt.show()
    if EXPORT_ANIMATION:
        animation.save('animation.gif', writer='ffmpeg')


def bfs_search(agent):
    route = [agent.vertex.coordinates]

    t = 0
    while not agent.is_at_destination():
        agent.vertex = agent.get_ideal_neighbor()
        route.append(agent.vertex.coordinates)

    return route


def generate_bfs_plan(agent):
    plan = [[]]

    route = bfs_search(agent)
    update_plan(plan, agent.agent_id, route)
    return plan


def generate_bfs_example(warehouse):
    source_id = random.randint(0, warehouse.number_of_sources - 1)
    destination_id = random.randint(0, warehouse.number_of_destinations - 1)
    source = warehouse.sources[source_id]
    destination = warehouse.destinations[destination_id]

    agent = Agent(0, source, destination)

    plan = generate_bfs_plan(agent)
    show_routes(warehouse, plan)








def update_plan(plan, i, route):
    if not route:
        return
    for step in route:
        plan[i].append(step)


def generate_rnd_plan(warehouse, agents, random_wait_at_source=False, sequential_exit=False):
    num_of_agents = len(agents)
    priority_order = random.sample(range(num_of_agents), num_of_agents)
    plan = [[] for _ in range(len(agents))]

    for route_number, i in enumerate(priority_order):
        agent = agents[i]
        agent_vertex = agent.vertex

        source_node = AStar.Node(agent_vertex, agent_vertex.destination_distance[agent.destination.destination_id], 0,
                                 None, True)
        destination_node = AStar.Node(agent.destination, 0, maxsize, None, False)
        a_star_framework = AStar(source_node, destination_node)

        route = a_star_framework.space_time_search(warehouse, agent, plan, route_number == 0,
                                                   route_number if sequential_exit else 0)
        update_plan(plan, i, route)
        if route_number % 5 == 0:
            print("Found route for", route_number + 1, "out of", num_of_agents, "agents")

    print("***")
    print("Done: Found route for", route_number + 1, "out of", num_of_agents, "agents")
    return plan


def generate_rnd_example(warehouse, title=""):
    sources = warehouse.sources
    num_of_sources = len(sources)
    num_of_waves = WAVES_PER_WAREHOUSE[warehouse.warehouse_id - 1]
    agents = []
    dest_ids = []
    for i in range(num_of_waves):
        destinations = random.choices(warehouse.destinations, k=num_of_sources)
        for j in range(num_of_sources):
            agents.append(Agent(i * num_of_sources + j, sources[j], destinations[j]))
            dest_ids.append(destinations[j].destination_id)

    t0 = time()
    plan = generate_rnd_plan(warehouse, agents)
    t1 = time()
    running_time = round(t1 - t0, 4)
    show_routes(warehouse, plan, running_time, "RND", dest_ids, title)


def add_obstacle_at_midpoint(added_obstacles, last_added_obstacle_midpoint, added_obstacle_size, obstacle_pattern):
    midpoint_x, midpoint_y = last_added_obstacle_midpoint[0], last_added_obstacle_midpoint[1]
    if obstacle_pattern == "cross":
        for i in range(added_obstacle_size):
            if (midpoint_x + ceil(added_obstacle_size / 2) - i, midpoint_y) not in added_obstacles:
                added_obstacles.add((midpoint_x + ceil(added_obstacle_size / 2) - i, midpoint_y))

            if (midpoint_x, midpoint_y + ceil(added_obstacle_size / 2) - i) not in added_obstacles:
                added_obstacles.add((midpoint_x, midpoint_y + ceil(added_obstacle_size / 2) - i))

    elif obstacle_pattern == "vertical_line":
        for i in range(2 * added_obstacle_size):
            if (midpoint_x + added_obstacle_size - i, midpoint_y) not in added_obstacles:
                added_obstacles.add((midpoint_x + added_obstacle_size - i, midpoint_y))

    elif obstacle_pattern == "horizontal_line":
        for i in range(2 * added_obstacle_size):
            if (midpoint_x, midpoint_y + added_obstacle_size - i) not in added_obstacles:
                added_obstacles.add((midpoint_x, midpoint_y + added_obstacle_size - i))

    else:  # square and dot pattern
        if obstacle_pattern == "dot":
            added_obstacle_size = 1

        for i in range(added_obstacle_size):
            if (midpoint_x + i, midpoint_y) not in added_obstacles:
                added_obstacles.add((midpoint_x + i, midpoint_y))

            if (midpoint_x, midpoint_y + i) not in added_obstacles:
                added_obstacles.add((midpoint_x, midpoint_y + i))

            if (midpoint_x + i, midpoint_y + added_obstacle_size - 1) not in added_obstacles:
                added_obstacles.add((midpoint_x + i, midpoint_y + added_obstacle_size - 1))

            if (midpoint_x + added_obstacle_size - 1, midpoint_y + i) not in added_obstacles:
                added_obstacles.add((midpoint_x + added_obstacle_size - 1, midpoint_y + i))


def generate_random_obstacles_restricted_plan(warehouse, agent, obstacle_patterns, max_routes=maxsize, initial_dist=0):
    # print("Generating random obstacles restricted plan, with obstacle patterns in", obstacle_patterns)
    # print("***")

    plan = []
    added_obstacles = set()
    added_obstacles_backup = set()
    route_backup = []
    agent_source = agent.vertex
    max_added_obstacle_size = ceil(min(warehouse.static_obstacle_length, warehouse.static_obstacle_width))

    source_node = AStar.Node(agent_source, agent_source.destination_distance[agent.destination.destination_id], 0,
                             None, True)
    destination_node = AStar.Node(agent.destination, 0, maxsize, None, False)
    a_star_framework = AStar(source_node, destination_node)

    tries = 0
    while len(plan) < max_routes and tries < PROGRESSIVELY_OBSTACLE_RESTRICTED_PLANS_MAX_TRIES:
        route = a_star_framework.search_with_added_obstacles(agent, added_obstacles)

        if route and len(route) + initial_dist <= warehouse.width + warehouse.length:
            tries = 0
            route_backup = route
            added_obstacles_backup = added_obstacles
            plan.append(route)
            if len(plan) % 10 == 0:
                print("Still generating, generated", len(plan), "routes")

        else:
            tries += 1
            added_obstacles = added_obstacles_backup
            route = route_backup

        obstacle_pattern = random.choice(obstacle_patterns)
        added_obstacle_size = random.randint(1, max_added_obstacle_size)
        min_idx = 4 * added_obstacle_size
        max_idx = len(route) - 1 - 4 * added_obstacle_size
        if max_idx - min_idx > 0:
            last_added_obstacle_midpoint = random.choice(route[4 * added_obstacle_size:-4 * added_obstacle_size])
        else:
            last_added_obstacle_midpoint = random.choice(route)

        if obstacle_pattern in {"square", "dot"}:
            last_added_obstacle_midpoint = (last_added_obstacle_midpoint[0] - ceil(added_obstacle_size / 2),
                                            last_added_obstacle_midpoint[1] - ceil(added_obstacle_size / 2))

        add_obstacle_at_midpoint(added_obstacles, last_added_obstacle_midpoint, added_obstacle_size,
                                 obstacle_pattern)
    return plan


def generate_random_obstacles_restricted_example(warehouse):
    source_id = random.randint(0, warehouse.number_of_sources - 1)
    destination_id = random.randint(0, warehouse.number_of_destinations - 1)
    source = warehouse.sources[source_id]
    destination = warehouse.destinations[destination_id]

    agent = Agent(0, source, destination)

    obstacle_patterns = ["cross", "square", "vertical_line", "horizontal_line", "dot"]
    # obstacle_patterns = ["horizontal_line"]
    plan = generate_random_obstacles_restricted_plan(warehouse, agent, obstacle_patterns)
    print("***")
    print("Done generating: Generated", len(plan), "routes")
    show_routes(warehouse, plan)


def generate_ideal_path_with_splits_plan(warehouse, source, destination):
    agent = Agent(0, source, destination)
    ideal_path = bfs_search(agent)

    plan = [ideal_path]
    obstacle_patterns = ["cross", "square", "vertical_line", "horizontal_line", "dot"]
    max_obstacle_size = min(warehouse.static_obstacle_length, warehouse.static_obstacle_width)
    split_step_and_size = max_obstacle_size
    agent_id = 1
    for i, coordinates in enumerate(ideal_path):
        split_on_every_step = False
        if split_on_every_step or i % split_step_and_size == 0:
            agent = Agent(agent_id, warehouse.vertices[coordinates[0]][coordinates[1]], destination)
            for agent_route in generate_random_obstacles_restricted_plan(agent, obstacle_patterns,
                                                                         4 * split_step_and_size, i):
                if not agent_route:
                    continue

                first_elements = ideal_path[:i - 1] if i != 0 else []
                plan.append(first_elements + agent_route)
            agent_id += 1

    return plan


def generate_ideal_path_with_splits_example(warehouse):
    source_id = random.randint(0, warehouse.number_of_sources - 1)
    destination_id = random.randint(0, warehouse.number_of_destinations - 1)
    source = warehouse.sources[source_id]
    destination = warehouse.destinations[destination_id]

    plan = generate_ideal_path_with_splits_plan(warehouse, source, destination)

    print("***")
    print("Done generating: Generated", len(plan), "routes")
    show_routes(warehouse, plan)


def get_warehouse_grid(warehouse):
    x_indices, y_indices = [], []

    x_step_size, y_step_size = floor(sqrt(warehouse.length)), floor(sqrt(warehouse.width))
    i = 0
    while i * x_step_size < warehouse.length:
        x_indices.append(i * x_step_size)
        i += 1
    if warehouse.length - 1 not in x_indices:
        x_indices.append(warehouse.length - 1)

    i = 0
    while i * y_step_size < warehouse.width:
        y_indices.append(i * y_step_size)
        i += 1
    if warehouse.width - 1 not in y_indices:
        y_indices.append(warehouse.width - 1)

    return x_indices, y_indices


def get_random_midpoints(warehouse):
    midpoints = set()
    x_indices, y_indices = get_warehouse_grid(warehouse)

    for i in range(len(x_indices) - 1):
        for j in range(len(y_indices) - 1):
            for _ in range(RANDOM_MIDPOINTS_MAX_TRIES):
                sampled_vertex = (random.randrange(x_indices[i], x_indices[i + 1]),
                                  random.randrange(y_indices[j], y_indices[j + 1]))
                if warehouse.is_valid_vertex(sampled_vertex[0], sampled_vertex[1]):
                    midpoints.add(sampled_vertex)
                    break

    return midpoints


def generate_midpoints_restricted_plan(warehouse, source, destination, is_split_at_midpoint=False):
    midpoints = get_random_midpoints(warehouse)

    plan = []
    for i, midpoint_coordinates in enumerate(midpoints):
        midpoint_vertex = warehouse.vertices[midpoint_coordinates[0]][midpoint_coordinates[1]]
        source_node = AStar.Node(source, distance(source.coordinates, midpoint_coordinates), 0, None, True)
        midpoint_node = AStar.Node(midpoint_vertex, 0, maxsize, None, False)
        a_star_framework = AStar(source_node, midpoint_node)

        route_to_midpoint = a_star_framework.classic_astar()
        if not route_to_midpoint:
            continue

        source_node = AStar.Node(midpoint_vertex, midpoint_vertex.destination_distance[destination.destination_id], 0,
                                 None, True)
        destination_node = AStar.Node(destination, 0, maxsize, None, False)
        a_star_framework = AStar(source_node, destination_node)

        route_from_midpoint = a_star_framework.classic_astar()
        if not route_from_midpoint:
            continue

        complete_route = route_to_midpoint + route_from_midpoint

        if len(complete_route) < warehouse.length + warehouse.width:
            if is_split_at_midpoint:
                obstacle_patterns = ["cross", "square", "vertical_line", "horizontal_line", "dot"]
                max_obstacle_size = min(warehouse.static_obstacle_length, warehouse.static_obstacle_width)
                split_step_size = max(2 * max_obstacle_size, 2)

                agent = Agent(i, midpoint_vertex, destination)
                for agent_route in generate_random_obstacles_restricted_plan(agent, obstacle_patterns, split_step_size,
                                                                             len(route_to_midpoint)):
                    plan.append(route_to_midpoint + agent_route)
            else:
                plan.append(complete_route)

    return plan


def generate_midpoints_restricted_example(warehouse, is_split_at_midpoint=False):
    source_id = random.randint(0, warehouse.number_of_sources - 1)
    destination_id = random.randint(0, warehouse.number_of_destinations - 1)
    source = warehouse.sources[source_id]
    destination = warehouse.destinations[destination_id]

    plan = generate_midpoints_restricted_plan(warehouse, source, destination, is_split_at_midpoint)

    print("***")
    print("Done generating: Generated", len(plan), "routes")
    show_routes(warehouse, plan)


def generate_midpoints_restricted_with_splits_example(warehouse):
    generate_midpoints_restricted_example(warehouse, True)


def neighborhood_sum_of_costs(plan, neighborhood):
    return sum([len(plan[i]) for i in neighborhood])


def neighborhood_makespan(plan, neighborhood):
    return max([len(plan[i]) for i in neighborhood])


def pick_better_plan(plan, backup_plan, neighborhood, cost_function=neighborhood_makespan):
    plan_cost = cost_function(plan, neighborhood)
    backup_plan_cost = cost_function(backup_plan, neighborhood)

    if plan_cost < backup_plan_cost:
        print("cost was", backup_plan_cost, "and is now", plan_cost)
        return plan
    return backup_plan


def replan(warehouse, plan, neighborhood, agents):
    for route_number, i in enumerate(neighborhood):
        agent = agents[i]
        agent_vertex = agent.vertex

        source_node = AStar.Node(agent_vertex, agent_vertex.destination_distance[agent.destination.destination_id], 0,
                                 None, True)
        destination_node = AStar.Node(agent.destination, 0, maxsize, None, False)
        a_star_framework = AStar(source_node, destination_node)

        route = a_star_framework.space_time_search(warehouse, agent, plan, route_number == 0, True)
        update_plan(plan, i, route)
    return plan


def erase_routes(plan, neighborhood):
    for i in neighborhood:
        plan[i] = []


def get_worst_makespan_agents(plan):
    worst_makespan = max(len(route) for route in plan)
    return [i for i in range(len(plan)) if len(plan[i]) == worst_makespan]


def pick_random_neighborhood(agents, plan):
    num_of_agents = len(agents)
    worst_makespan_agents = get_worst_makespan_agents(plan)
    random_sample = random.sample(range(num_of_agents), 2 * round(sqrt(num_of_agents)))

    neighborhood = worst_makespan_agents + random_sample
    random.shuffle(neighborhood)
    return neighborhood


def generate_lns_rnd_plan(agents, neighborhood_picking_function=pick_random_neighborhood):
    # agents = sort_agents_non_crossing_diagonals(agents)
    plan = generate_rnd_plan(agents, False, True)

    for _ in range(LNS_ITERATIONS):
        plan_backup = plan.copy()

        # neighborhood contains the list of indexes of agents to replan for
        neighborhood = neighborhood_picking_function(agents, plan)
        erase_routes(plan, neighborhood)
        plan = replan(plan, neighborhood, agents)
        plan = pick_better_plan(plan, plan_backup, neighborhood)

    return plan


def generate_lns_rnd_example(warehouse, title=""):
    sources = warehouse.sources
    num_of_sources = len(sources)
    num_of_waves = WAVES_PER_WAREHOUSE[warehouse.warehouse_id - 1]
    agents = []
    dest_ids = []
    for i in range(num_of_waves):
        destinations = random.choices(warehouse.destinations, k=num_of_sources)
        for j in range(num_of_sources):
            agents.append(Agent(i * num_of_sources + j, sources[j], destinations[j]))
            dest_ids.append(destinations[j].destination_id)

    print("Generating LNS-RND plan, with (num_of_waves) =", num_of_waves)
    print("***")
    t0 = time()
    plan = generate_lns_rnd_plan(agents, pick_random_neighborhood)
    t1 = time()
    running_time = round(t1 - t0, 4)
    show_routes(warehouse, plan, running_time, "LNS-RND", dest_ids, title)


def ordered_by_destination_id(agents):
    sorted_agents = sorted(agents, key=Agent.get_destination_id)
    sorted_agent_ids = [agent.agent_id for agent in sorted_agents]
    # num_of_agents = len(agents)
    # agent_ids = list(range(num_of_agents))
    # agent_ids.sort(key=Agent.get_destination_id)
    return sorted_agent_ids


def ordered_by_source_id(agents):
    sorted_agents = sorted(agents, key=Agent.get_source_id)
    sorted_agent_ids = [agent.agent_id for agent in sorted_agents]
    # num_of_agents = len(agents)
    # agent_ids = list(range(num_of_agents))
    # agent_ids.sort(key=Agent.get_destination_id)
    return sorted_agent_ids


def ordered_by_source_then_destination_id(agents):
    # sorted_agents = sorted(agents, key=cmp_to_key(Agent.comparator_source_destination_id))
    sorted_agents = sorted(agents, key=Agent.get_destination_id)
    sorted_agents = sorted(sorted_agents, key=Agent.get_source_id)
    # print(sorted_agents2 == sorted_agents)
    sorted_agent_ids = [agent.agent_id for agent in sorted_agents]
    return sorted_agent_ids


def generate_ordered_by_destination_plan(warehouse, agents):
    num_of_agents = len(agents)
    priority_order = ordered_by_source_then_destination_id(agents)
    plan = [[] for _ in range(num_of_agents)]

    for route_number, i in enumerate(priority_order):
        agent = agents[i]
        agent_vertex = agent.vertex

        source_node = AStar.Node(agent_vertex, agent_vertex.destination_distance[agent.destination.destination_id], 0,
                                 None, True)
        destination_node = AStar.Node(agent.destination, 0, maxsize, None, False)
        a_star_framework = AStar(source_node, destination_node)

        route = a_star_framework.space_time_search(warehouse, agent, plan, route_number == 0)
        update_plan(plan, i, route)
        if route_number % 5 == 0:
            print("Found route for", route_number + 1, "out of", num_of_agents, "agents")

    print("***")
    print("Done: Found route for", route_number + 1, "out of", num_of_agents, "agents")
    return plan


def generate_ordered_by_destination_example(warehouse):
    sources = warehouse.sources
    num_of_sources = len(sources)
    num_of_waves = WAVES_PER_WAREHOUSE[warehouse.warehouse_id - 1]
    agents = []
    dest_ids = []
    for i in range(num_of_waves):
        destinations = random.choices(warehouse.destinations, k=num_of_sources)
        for j in range(num_of_sources):
            agents.append(Agent(i * num_of_sources + j, sources[j], destinations[j]))
            dest_ids.append(destinations[j].destination_id)

    t0 = time()
    plan = generate_ordered_by_destination_plan(agents)
    t1 = time()
    running_time = round(t1 - t0, 4)
    show_routes(warehouse, plan, running_time, "RND", dest_ids)


def main():
    warehouse_types = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
    warehouse = generate_warehouse(warehouse_types["small structured"])

    # generate_bfs_example(warehouse)
    generate_rnd_example(warehouse, "")
    # generate_ordered_by_destination_example(warehouse)
    # generate_lns_rnd_example(warehouse, "Title")
    # generate_random_obstacles_restricted_example(warehouse)
    # generate_ideal_path_with_splits_example(warehouse)

    # generate_midpoints_restricted_example(warehouse)
    # generate_midpoints_restricted_with_splits_example(warehouse)


if __name__ == "__main__":
    main()

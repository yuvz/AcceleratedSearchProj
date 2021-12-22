from time import time
from Environment import *
from EnvironmentUtils import *
from Utils import *
from Visualization import show_plan
from math import ceil, sqrt, floor
from PlanGeneration import generate_example

WAVES_PER_WAREHOUSE = [5, 1, 10, 1]

RANDOM_SCHEDULING_ENABLED = False

PROGRESSIVELY_OBSTACLE_RESTRICTED_PLANS_MAX_TRIES = 5
RANDOM_MIDPOINTS_MAX_TRIES = 5


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


def update_plan(plan, i, route):
    if not route:
        return
    for step in route:
        plan[i].append(step)


# def generate_rnd_example(warehouse, title=""):
#     agents = generate_rand_agents(warehouse, WAVES_PER_WAREHOUSE)
#     t0 = time()
#     plan = generate_rnd_plan(warehouse, agents)
#     t1 = time()
#     running_time = round(t1 - t0, 4)
#     show_plan(warehouse, plan, running_time, "RND", title)


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
    show_plan(warehouse, plan)


def generate_ideal_path_with_splits_plan(warehouse, source, destination):
    ideal_path = (BFS(source, destination).generate_plan())[0]

    plan = [ideal_path]
    obstacle_patterns = ["cross", "square", "vertical_line", "horizontal_line", "dot"]
    max_obstacle_size = min(warehouse.static_obstacle_length, warehouse.static_obstacle_width)
    split_step_and_size = max_obstacle_size
    agent_id = 1
    for i, coordinates in enumerate(ideal_path):
        split_on_every_step = False
        if split_on_every_step or i % split_step_and_size == 0:
            agent = Agent(agent_id, warehouse.vertices[coordinates[0]][coordinates[1]], destination)
            for agent_route in generate_random_obstacles_restricted_plan(warehouse, agent, obstacle_patterns,
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
    show_plan(warehouse, plan)


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
                for agent_route in generate_random_obstacles_restricted_plan(warehouse, agent, obstacle_patterns,
                                                                             split_step_size, len(route_to_midpoint)):
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
    show_plan(warehouse, plan)


def generate_midpoints_restricted_with_splits_example(warehouse):
    generate_midpoints_restricted_example(warehouse, True)


def main():
    warehouse_types = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
    warehouse = generate_warehouse(warehouse_types["first paper"])

    algorithm_name = "LNS_RND"  # currently works with BFS, RND, LNS_RND
    title = "Visualization title"
    plan, running_time = generate_example(warehouse, WAVES_PER_WAREHOUSE, algorithm_name)

    show_plan(warehouse, plan, running_time, algorithm_name, title)

    # generate_random_obstacles_restricted_example(warehouse)
    # plan = generate_ideal_path_with_splits_example(warehouse)

    # generate_midpoints_restricted_example(warehouse)
    # generate_midpoints_restricted_with_splits_example(warehouse)


if __name__ == "__main__":
    main()

import random
from math import ceil
from sys import maxsize

from AStar import AStar
PROGRESSIVELY_OBSTACLE_RESTRICTED_PLANS_MAX_TRIES = 5
RANDOM_MIDPOINTS_MAX_TRIES = 5


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


def generate_random_obstacles_restricted_plan(warehouse, routing_request, obstacle_patterns, max_routes=maxsize, initial_dist=0):
    # print("Generating random obstacles restricted plan, with obstacle patterns in", obstacle_patterns)
    # print("***")

    plan = []
    added_obstacles = set()
    added_obstacles_backup = set()
    route_backup = []
    routing_request_source = routing_request.source
    max_added_obstacle_size = ceil(min(warehouse.static_obstacle_length, warehouse.static_obstacle_width))

    source_node = AStar.Node(routing_request_source, routing_request_source.destination_distance[routing_request.destination.destination_id], 0,
                             None, True)
    destination_node = AStar.Node(routing_request.destination, 0, maxsize, None, False)
    a_star_framework = AStar(source_node, destination_node)

    tries = 0
    while len(plan) < max_routes and tries < PROGRESSIVELY_OBSTACLE_RESTRICTED_PLANS_MAX_TRIES:
        route = a_star_framework.search_with_added_obstacles(routing_request, added_obstacles)

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

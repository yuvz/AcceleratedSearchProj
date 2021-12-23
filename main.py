from BFS import BFS
from RoutingRequest import *
from EnvironmentUtils import *
from Utils import *
from Visualization import show_plan_as_animation, show_plan_as_image
from math import ceil, sqrt, floor
from ExampleGeneration import generate_example


WAVES_PER_WAREHOUSE = [10, 1, 10, 1]

RANDOM_SCHEDULING_ENABLED = False


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
#     routing_requests = generate_rand_routing_requests(warehouse, WAVES_PER_WAREHOUSE)
#     t0 = time()
#     plan = generate_rnd_plan(warehouse, routing_requests)
#     t1 = time()
#     running_time = round(t1 - t0, 4)
#     show_plan(warehouse, plan, running_time, "RND", title)








def generate_ideal_path_with_splits_plan(warehouse, source, destination):
    ideal_path = (BFS(source, destination).generate_plan())[0]

    plan = [ideal_path]
    obstacle_patterns = ["cross", "square", "vertical_line", "horizontal_line", "dot"]
    max_obstacle_size = min(warehouse.static_obstacle_length, warehouse.static_obstacle_width)
    split_step_and_size = max_obstacle_size
    routing_request_id = 1
    for i, coordinates in enumerate(ideal_path):
        split_on_every_step = False
        if split_on_every_step or i % split_step_and_size == 0:
            routing_request = RoutingRequest(routing_request_id, warehouse.vertices[coordinates[0]][coordinates[1]], destination)
            for routing_request_route in generate_random_obstacles_restricted_plan(warehouse, routing_request, obstacle_patterns,
                                                                         4 * split_step_and_size, i):
                if not routing_request_route:
                    continue

                first_elements = ideal_path[:i - 1] if i != 0 else []
                plan.append(first_elements + routing_request_route)
            routing_request_id += 1

    return plan


def generate_ideal_path_with_splits_example(warehouse):
    source_id = random.randint(0, warehouse.number_of_sources - 1)
    destination_id = random.randint(0, warehouse.number_of_destinations - 1)
    source = warehouse.sources[source_id]
    destination = warehouse.destinations[destination_id]

    plan = generate_ideal_path_with_splits_plan(warehouse, source, destination)

    print("***")
    print("Done generating: Generated", len(plan), "routes")
    # show_plan(warehouse, plan)


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

                routing_request = RoutingRequest(i, midpoint_vertex, destination)
                for routing_request_route in generate_random_obstacles_restricted_plan(warehouse, routing_request, obstacle_patterns,
                                                                             split_step_size, len(route_to_midpoint)):
                    plan.append(route_to_midpoint + routing_request_route)
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
    # show_plan(warehouse, plan)


def generate_midpoints_restricted_with_splits_example(warehouse):
    generate_midpoints_restricted_example(warehouse, True)


def main():
    warehouse_types = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
    warehouse = generate_warehouse(warehouse_types["small structured"])

    algorithm_name = "K-ROR"  # currently works with BFS, RND, LNS_RND
    plan, running_time = generate_example(warehouse, WAVES_PER_WAREHOUSE, algorithm_name)

    title = "Visualization title"
    export_visualuzation = False

    # show_plan_as_animation(warehouse, plan, running_time, algorithm_name, title, export_visualuzation)
    show_plan_as_image(warehouse, plan, running_time, algorithm_name, title, export_visualuzation)
    # TODO: export_plan_to_csv(plan, running_time)

    # generate_random_obstacles_restricted_example(warehouse)
    # plan = generate_ideal_path_with_splits_example(warehouse)

    # generate_midpoints_restricted_example(warehouse)
    # generate_midpoints_restricted_with_splits_example(warehouse)


if __name__ == "__main__":
    main()

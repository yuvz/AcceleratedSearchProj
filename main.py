from DatabaseBuilding import create_routes_from_source_to_destination_by_MPR_WS, export_routes_to_csv, export_warehouse_to_csv, import_csv_to_routes
from ExampleGeneration import generate_rand_example
from EnvironmentUtils import generate_warehouse
from Visualization import show_plan_as_animation, show_plan_as_image
    
RANDOM_SCHEDULING_ENABLED = False
TEST_ROUTING_REQUESTS = [(0, 3), (1, 3), (2, 3), (3, 5), (4, 1), (5, 2), (6, 5), (0, 3), (1, 6), (2, 4), (3, 4), (4, 2),
                         (5, 2), (6, 0), (0, 6), (1, 5), (2, 0), (3, 2), (4, 1), (5, 1), (6, 6), (0, 0), (1, 0), (2, 0),
                         (3, 6), (4, 5), (5, 2), (6, 3), (0, 4), (1, 1), (2, 0), (3, 0), (4, 3), (5, 2), (6, 1), (0, 6),
                         (1, 1), (2, 5), (3, 4), (4, 3), (5, 6), (6, 1), (0, 5), (1, 1), (2, 0), (3, 0), (4, 2), (5, 2),
                         (6, 2), (0, 4), (1, 3), (2, 6), (3, 5), (4, 3), (5, 4), (6, 1), (0, 2), (1, 4), (2, 6), (3, 0),
                         (4, 1), (5, 4), (6, 2), (0, 5), (1, 6), (2, 1), (3, 4), (4, 3), (5, 6), (6, 5)]


def generate_example(warehouse, algorithm_name, is_show_animation=True, is_show_image=False,
                     is_export_visualization=False): 
    plan, running_time = generate_rand_example(warehouse, algorithm_name)
    title = "Visualization title"

    if is_show_animation:
        show_plan_as_animation(warehouse, plan, algorithm_name, running_time, title, is_export_visualization)
    if is_show_image:
        show_plan_as_image(warehouse, plan, algorithm_name, running_time, title, is_export_visualization)


def generate_routes(warehouse, algorithm_name="MPR_WS", source_id=0, destination_id=0):
    source, destination = warehouse.sources[source_id], warehouse.destinations[destination_id]
    routes = create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination)

    # show_plan_as_animation(warehouse, routes, algorithm_name)

    export_routes_to_csv(algorithm_name, source_id, destination_id, routes)  # TODO: @NimrodMarom


def main():
    """
    Supported values for algorithm_name: [BFS, RND, LNS_RND, CBS, ROR, k-ROR, IPWS, k-IPWS, MPR, k-MPR, MPR_WS,
    k-MPR_WS] - check generate_example() in ExampleGeneration.py to see which algorithm is referred to by each abbr.
    """
    warehouse_types = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
    warehouse = generate_warehouse(warehouse_types["small structured"])
    
    export_warehouse_to_csv(warehouse)

    generate_example(warehouse, "MPR_WS")
    generate_routes(warehouse, "MPR_WS", 2, 1)

    # plan, running_time = generate_rand_example(warehouse, algorithm_name)

    # source_id, destination_id = 2, 1
    # source, destination = warehouse.sources[source_id], warehouse.destinations[destination_id]
    # plan = create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination)
    # plan, running_time = generate_routes_from_source_to_destination(warehouse, algorithm_name, source_id, destination_id)
    generate_example(warehouse, "LNS_RND", TEST_ROUTING_REQUESTS)
    # generate_example(warehouse, "ROR")


if __name__ == "__main__":
    main()

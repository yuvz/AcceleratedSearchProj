from DatabaseBuilding import create_routes_from_source_to_destination_by_MPR_WS, export_routes_to_csv
from ExampleGeneration import generate_rand_example
from EnvironmentUtils import generate_warehouse, generate_rand_routing_requests
from Visualization import show_plan_as_animation, show_plan_as_image

RANDOM_SCHEDULING_ENABLED = False


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

    export_routes_to_csv(algorithm_name, source_id, destination_id, routes)     # TODO: @NimrodMarom


def main():
    """
    Supported values for algorithm_name: [BFS, RND, LNS_RND, ROR, k-ROR, IPWS, k-IPWS, MPR, k-MPR, MPR_WS, k-MPR_WS,
    CBS] - check generate_example() in ExampleGeneration.py to see which algorithm is referred to by each abbr.
    """

    warehouse_types = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
    warehouse = generate_warehouse(warehouse_types["small structured"])

    generate_example(warehouse, "MPR_WS")
    # generate_routes(warehouse, "MPR_WS", 2, 1)

    # plan, running_time = generate_rand_example(warehouse, algorithm_name)

    # source_id, destination_id = 2, 1
    # source, destination = warehouse.sources[source_id], warehouse.destinations[destination_id]
    # plan = create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination)
    # plan, running_time = generate_routes_from_source_to_destination(warehouse, algorithm_name, source_id, destination_id)


if __name__ == "__main__":
    main()

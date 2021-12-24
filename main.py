from DatabaseBuilding import create_routes_from_source_to_destination_by_MPR_WS
from EnvironmentUtils import generate_warehouse
from ExampleGeneration import generate_rand_example
from RouteGeneration import generate_routes_from_source_to_destination
from Visualization import show_plan_as_animation, show_plan_as_image

RANDOM_SCHEDULING_ENABLED = False


def generate_example(warehouse, algorithm_name, is_show_animation=True, is_show_image=False,
                     is_export_visualization=False):
    plan, running_time = generate_rand_example(warehouse, algorithm_name)
    title = "Visualization title"

    if is_show_animation:
        show_plan_as_animation(warehouse, plan, running_time, algorithm_name, title, is_export_visualization)
    if is_show_image:
        show_plan_as_image(warehouse, plan, running_time, algorithm_name, title, is_export_visualization)


def generate_routes(warehouse, algorithm_name="MPR_WS", source_id=0, destination_id=0, generate_for_all_combinations=False):
    source, destination = warehouse.sources[source_id], warehouse.destinations[destination_id]
    routes = create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination)
    # TODO: export_routes_to_csv(routes, algorithm_name) - @NimrodMarom


def main():
    """
    Supported values for algorithm_name: [BFS, RND, LNS_RND, ROR, k-ROR, IPWS, k-IPWS, MPR, k-MPR, MPR_WS, k-MPR_WS]
    - check generate_example() in ExampleGeneration.py to see which algorithm is referred to by each abbr.
    """

    warehouse_types = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
    warehouse = generate_warehouse(warehouse_types["small structured"])

    # generate_example(warehouse, "MPR_WS")
    generate_routes(warehouse, "MPR_WS", 2, 1, False)

    # plan, running_time = generate_rand_example(warehouse, algorithm_name)

    # source_id, destination_id = 2, 1
    # source, destination = warehouse.sources[source_id], warehouse.destinations[destination_id]
    # plan = create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination)
    # plan, running_time = generate_routes_from_source_to_destination(warehouse, algorithm_name, source_id, destination_id)


if __name__ == "__main__":
    main()

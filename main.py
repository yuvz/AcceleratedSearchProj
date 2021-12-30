from DatabaseBuilding import build_routes_for_database, build_tagged_examples_for_database, export_plan_to_csv
from ExampleGeneration import generate_example
from EnvironmentUtils import generate_warehouse
from Visualization import visualize_plan

WAREHOUSE_TYPES = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
VISUALIZE_RESULT = True
EXPORT_RESULT_TO_CSV = False

FIFTY_WAVE_ROUTING_REQUESTS_TEST = [(0, 4), (1, 1), (2, 5), (3, 1), (4, 5), (5, 4), (6, 2), (0, 5), (1, 2), (2, 4), (3, 5), (4, 5), (5, 4), (6, 6), (0, 5), (1, 2), (2, 4), (3, 3), (4, 2), (5, 0), (6, 1), (0, 2), (1, 1), (2, 3), (3, 6), (4, 1), (5, 6), (6, 1), (0, 2), (1, 0), (2, 1), (3, 6), (4, 2), (5, 5), (6, 5), (0, 5), (1, 5), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4), (0, 1), (1, 3), (2, 0), (3, 1), (4, 5), (5, 3), (6, 3), (0, 5), (1, 2), (2, 3), (3, 6), (4, 0), (5, 5), (6, 1), (0, 2), (1, 3), (2, 6), (3, 3), (4, 6), (5, 4), (6, 3), (0, 2), (1, 3), (2, 6), (3, 2), (4, 4), (5, 6), (6, 5), (0, 1), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 5), (0, 6), (1, 5), (2, 1), (3, 4), (4, 4), (5, 1), (6, 4), (0, 4), (1, 5), (2, 3), (3, 2), (4, 1), (5, 2), (6, 0), (0, 5), (1, 0), (2, 1), (3, 5), (4, 2), (5, 0), (6, 1), (0, 0), (1, 5), (2, 3), (3, 2), (4, 1), (5, 2), (6, 1), (0, 3), (1, 0), (2, 4), (3, 0), (4, 2), (5, 5), (6, 6), (0, 1), (1, 6), (2, 1), (3, 2), (4, 6), (5, 1), (6, 3), (0, 0), (1, 0), (2, 1), (3, 1), (4, 0), (5, 4), (6, 1), (0, 4), (1, 1), (2, 3), (3, 6), (4, 6), (5, 2), (6, 6), (0, 1), (1, 0), (2, 2), (3, 3), (4, 2), (5, 3), (6, 3), (0, 2), (1, 1), (2, 2), (3, 2), (4, 5), (5, 2), (6, 0), (0, 4), (1, 6), (2, 0), (3, 6), (4, 0), (5, 6), (6, 0), (0, 4), (1, 2), (2, 1), (3, 5), (4, 5), (5, 2), (6, 3), (0, 6), (1, 4), (2, 2), (3, 2), (4, 3), (5, 0), (6, 4), (0, 4), (1, 6), (2, 5), (3, 1), (4, 3), (5, 4), (6, 5), (0, 6), (1, 4), (2, 5), (3, 5), (4, 1), (5, 1), (6, 4), (0, 3), (1, 1), (2, 1), (3, 5), (4, 2), (5, 2), (6, 5), (0, 2), (1, 3), (2, 3), (3, 1), (4, 5), (5, 6), (6, 6), (0, 3), (1, 1), (2, 3), (3, 4), (4, 3), (5, 0), (6, 6), (0, 3), (1, 0), (2, 5), (3, 3), (4, 3), (5, 1), (6, 5), (0, 6), (1, 3), (2, 4), (3, 4), (4, 1), (5, 5), (6, 2), (0, 1), (1, 3), (2, 6), (3, 2), (4, 3), (5, 3), (6, 5), (0, 5), (1, 5), (2, 6), (3, 3), (4, 4), (5, 2), (6, 5), (0, 5), (1, 6), (2, 2), (3, 6), (4, 6), (5, 0), (6, 0), (0, 3), (1, 4), (2, 3), (3, 4), (4, 1), (5, 6), (6, 4), (0, 6), (1, 0), (2, 6), (3, 4), (4, 3), (5, 5), (6, 4), (0, 0), (1, 1), (2, 5), (3, 3), (4, 5), (5, 3), (6, 3), (0, 4), (1, 0), (2, 1), (3, 6), (4, 5), (5, 3), (6, 6), (0, 2), (1, 5), (2, 3), (3, 0), (4, 6), (5, 6), (6, 6), (0, 3), (1, 4), (2, 5), (3, 5), (4, 1), (5, 6), (6, 1), (0, 6), (1, 6), (2, 5), (3, 2), (4, 5), (5, 3), (6, 6), (0, 3), (1, 1), (2, 6), (3, 6), (4, 4), (5, 0), (6, 6), (0, 5), (1, 1), (2, 5), (3, 5), (4, 0), (5, 5), (6, 4), (0, 5), (1, 0), (2, 4), (3, 1), (4, 4), (5, 2), (6, 0), (0, 2), (1, 0), (2, 6), (3, 2), (4, 2), (5, 5), (6, 4), (0, 6), (1, 4), (2, 2), (3, 2), (4, 2), (5, 6), (6, 0), (0, 6), (1, 1), (2, 2), (3, 0), (4, 5), (5, 2), (6, 6), (0, 0), (1, 4), (2, 3), (3, 3), (4, 1), (5, 5), (6, 6), (0, 3), (1, 1), (2, 6), (3, 3), (4, 1), (5, 3), (6, 0), (0, 6), (1, 3), (2, 0), (3, 3), (4, 6), (5, 0), (6, 4)]

TEN_WAVE_ROUTING_REQUESTS_TEST = [(0, 3), (1, 3), (2, 3), (3, 5), (4, 1), (5, 2), (6, 5),
                                  (0, 3), (1, 6), (2, 4), (3, 4), (4, 2), (5, 2), (6, 0),
                                  (0, 6), (1, 5), (2, 0), (3, 2), (4, 1), (5, 1), (6, 6),
                                  (0, 0), (1, 0), (2, 0), (3, 6), (4, 5), (5, 2), (6, 3),
                                  (0, 4), (1, 1), (2, 0), (3, 0), (4, 3), (5, 2), (6, 1),
                                  (0, 6), (1, 1), (2, 5), (3, 4), (4, 3), (5, 6), (6, 1),
                                  (0, 5), (1, 1), (2, 0), (3, 0), (4, 2), (5, 2), (6, 2),
                                  (0, 4), (1, 3), (2, 6), (3, 5), (4, 3), (5, 4), (6, 1),
                                  (0, 2), (1, 4), (2, 6), (3, 0), (4, 1), (5, 4), (6, 2),
                                  (0, 5), (1, 6), (2, 1), (3, 4), (4, 3), (5, 6), (6, 5)]

TWO_WAVE_ROUTING_REQUEST_TEST = [(0, 6), (1, 6), (2, 6), (3, 2), (4, 6), (5, 2), (6, 3),
                                 (0, 0), (1, 6), (2, 3), (3, 6), (4, 6), (5, 2), (6, 4)]

ONE_WAVE_ROUTING_REQUEST_TEST = [(0, 6), (1, 6), (2, 6), (3, 2), (4, 6), (5, 2), (6, 3)]

CSV_GENERATION_ROUTING_REQUEST = [(2, 1)]


def main():
    """
    Supported values for algorithm_name: [BFS, RND, LNS_RND, CBS, ROR, k-ROR, IPWS, k-IPWS, MPR, k-MPR, MPR_WS,
    k-MPR_WS, sample_database] - check generate_example() in ExampleGeneration.py to see which algorithm is referred to by each abbr.
    """
    warehouse = generate_warehouse(WAREHOUSE_TYPES["small structured"])
    algorithm_name = "sample_database"

    # for _ in range(10):
    #     build_routes_for_database(warehouse)
    # plan, running_time, routing_requests = generate_example(warehouse, algorithm_name, ONE_WAVE_ROUTING_REQUEST_TEST)
    # plan, running_time, routing_requests = generate_example(warehouse, algorithm_name, TWO_WAVE_ROUTING_REQUEST_TEST)
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name)
    # build_tagged_examples_for_database(warehouse)

    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = True
        visualize_plan(warehouse, plan, algorithm_name, running_time, visualization_type, title,
                       is_export_visualization)

    if EXPORT_RESULT_TO_CSV:
        export_plan_to_csv(algorithm_name, plan, warehouse)


if __name__ == "__main__":
    main()

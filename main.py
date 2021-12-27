from DatabaseBuilding import export_plan_to_csv, export_routes_source_to_dest_to_csv, export_all_routes_to_csv, import_csv_to_routes
from ExampleGeneration import generate_example
from EnvironmentUtils import generate_warehouse
from Visualization import show_plan_as_animation, show_plan_as_image, visualize_plan
from Warehouse import Warehouse
    
RANDOM_SCHEDULING_ENABLED = False
TEST_ROUTING_REQUESTS = [(0, 3), (1, 3), (2, 3), (3, 5), (4, 1), (5, 2), (6, 5), (0, 3), (1, 6), (2, 4), (3, 4), (4, 2),
                         (5, 2), (6, 0), (0, 6), (1, 5), (2, 0), (3, 2), (4, 1), (5, 1), (6, 6), (0, 0), (1, 0), (2, 0),
                         (3, 6), (4, 5), (5, 2), (6, 3), (0, 4), (1, 1), (2, 0), (3, 0), (4, 3), (5, 2), (6, 1), (0, 6),
                         (1, 1), (2, 5), (3, 4), (4, 3), (5, 6), (6, 1), (0, 5), (1, 1), (2, 0), (3, 0), (4, 2), (5, 2),
                         (6, 2), (0, 4), (1, 3), (2, 6), (3, 5), (4, 3), (5, 4), (6, 1), (0, 2), (1, 4), (2, 6), (3, 0),
                         (4, 1), (5, 4), (6, 2), (0, 5), (1, 6), (2, 1), (3, 4), (4, 3), (5, 6), (6, 5)]

WAREHOUSE_TYPES = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
VISUALIZE_RESULT = False
EXPORT_RESULT_TO_CSV = True

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

CSV_GENERATION_ROUTING_REQUEST = [(2, 1)]

def main():
    """
    Supported values for algorithm_name: [BFS, RND, LNS_RND, CBS, ROR, k-ROR, IPWS, k-IPWS, MPR, k-MPR, MPR_WS,
    k-MPR_WS] - check generate_example() in ExampleGeneration.py to see which algorithm is referred to by each abbr.
    """
    warehouse = generate_warehouse(WAREHOUSE_TYPES["small structured"])
    algorithm_name = "RND"

    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name, TWO_WAVE_ROUTING_REQUEST_TEST)
    # plan, running_time, routing_requests = generate_example(warehouse, algorithm_name)
    import_csv_to_routes('./csv_files/warehouse_3/routes/routes_from_0_to_1.csv')
    source_dest_list = [(0,1), (0, 3), (1,2), (4, 4), (0,4), (1,3), (2,2), (2,4), (1,0)] # assuming there are tupples of (Source, Dest)
    # source_dest_list = create_tupples_list()
    for tupple in source_dest_list:
        routes, _, _ = generate_example(warehouse, 'MPR', [tupple])
        export_routes_source_to_dest_to_csv(algorithm_name, tupple[0], tupple[1], routes, warehouse)  
    export_all_routes_to_csv(warehouse, source_dest_list)

    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, algorithm_name, running_time, visualization_type, title,
                       is_export_visualization)

    if EXPORT_RESULT_TO_CSV:
        export_plan_to_csv(algorithm_name, plan, warehouse)


if __name__ == "__main__":
    main()

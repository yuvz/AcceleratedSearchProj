from DatabaseInterface import initialize_database_perliminary_files, generate_path_for_given_arrival_time, \
    generate_path_database, generate_approximately_matching_deviation_factor_path_via_midpoint, run_experiment
from ExampleGeneration import generate_example
from EnvironmentUtils import generate_warehouse
from Visualization import visualize_plan
from time import time

WAREHOUSE_TYPES = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
HUGE_WAREHOUSE_IDS = [200, 201, 202, 203, 204, 205]
VISUALIZE_RESULT = True
EXPORT_RESULT_TO_CSV = False


def main():
    """
    Run initialize_database_perliminary_files first
        -> Then you can start generating the database with generate_path_database
            -> Then you can start sampling the database with sample_path_database

    You can also use generate_example regardless of the database mentioned above.
        Check the generate_example code to see what input to supply.
    """
    warehouse = generate_warehouse(203)
    initialize_database_perliminary_files(warehouse)

    t0 = time()
    plan, vertex_conflicts, swapping_conflicts = run_experiment(warehouse, 10)
    t1 = time()

    running_time = round(t1 - t0, 2)
    algorithm_name = f"run_experiment"

    # # plan = generate_path_database(warehouse, 10, [1.01],
    # #                               generate_approximately_matching_deviation_factor_path_via_midpoint)
    # # plan = sample_path_database(warehouse, 15, 25, 1.5)
    # running_time = round(t1 - t0, 2)
    # algorithm_name = ""
    #
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = f"vertex_conflicts={vertex_conflicts}, swapping_conflicts={swapping_conflicts}"
        is_export_visualization = True
        # visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title)

        visualization_type = "image"
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)


if __name__ == "__main__":
    main()

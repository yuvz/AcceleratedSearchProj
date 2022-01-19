from ConflictsByNumberOfAgentsExperiment import run_experiment, \
    run_experiments_to_generate_main_data_file, generate_conflict_probability_by_number_of_agents_data, \
    generate_conflict_probability_by_number_of_agents_visualization, generate_vertex_conflict_heatmap_data, \
    generate_vertex_conflict_heatmap_visualization, generate_swapping_conflict_heatmap_data, \
    generate_swapping_conflict_heatmap_visualization
from DatabaseInterface import initialize_database_preliminary_files

from ExampleGeneration import generate_example
from EnvironmentUtils import generate_warehouse
from Visualization import visualize_plan
from time import time

WAREHOUSE_TYPES = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
HUGE_WAREHOUSE_IDS = [200, 201, 202, 203, 204, 205]
VISUALIZE_RESULT = True
EXPORT_RESULT_TO_CSV = False


def previous_algorithms_template(warehouse_id):
    warehouse = generate_warehouse(warehouse_id)

    t0 = time()
    routing_requests, plan, vertex_conflicts, swapping_conflicts = run_experiment(warehouse, 10)
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
        title = f"vertex_conflicts={vertex_conflicts},\n swapping_conflicts={swapping_conflicts}"
        is_export_visualization = True
        # visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title)

        visualization_type = "image"
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)


def generate_database(warehouse_id, max_number_of_agents, number_of_agents_incrementation_step=1,
                      number_of_samples=1000):
    warehouse = generate_warehouse(warehouse_id)
    initialize_database_preliminary_files(warehouse)

    for i in range(1, max_number_of_agents, number_of_agents_incrementation_step):
        run_experiments_to_generate_main_data_file(warehouse, i, number_of_samples)


def generate_conflict_probability_by_number_of_agents_scatterplot(warehouse_id):
    generate_conflict_probability_by_number_of_agents_data(warehouse_id)
    generate_conflict_probability_by_number_of_agents_visualization(warehouse_id)


def generate_vertex_conflict_heatmap(warehouse_id):
    warehouse = generate_warehouse(warehouse_id)
    generate_vertex_conflict_heatmap_data(warehouse)
    generate_vertex_conflict_heatmap_visualization(warehouse_id)


def generate_swapping_conflict_heatmap(warehouse_id):
    warehouse = generate_warehouse(warehouse_id)
    generate_swapping_conflict_heatmap_data(warehouse)
    generate_swapping_conflict_heatmap_visualization(warehouse_id)


def main():
    """
    Run initialize_database_preliminary_files first
        -> Then you can start generating the database with generate_path_database
            -> Then you can start sampling the database with sample_path_database

    You can also use generate_example regardless of the database mentioned above.
        Check the generate_example code to see what input to supply.
    """
    # running suggestion with warehouse_id=203. Please pick any warehouse_id between 201-206 for your runs.
    generate_database(203, 400, 20)
    generate_conflict_probability_by_number_of_agents_scatterplot(203)
    generate_vertex_conflict_heatmap(203)
    generate_swapping_conflict_heatmap(203)


if __name__ == "__main__":
    main()

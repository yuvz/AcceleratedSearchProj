from DatabaseInterface import initialize_database_preliminary_files

from ExampleGeneration import generate_example
from EnvironmentUtils import generate_warehouse
from Visualization import visualize_plan
from time import time

SINGLE_SOURCE_DESTINATION = False

if SINGLE_SOURCE_DESTINATION:
    from SingleSourceDestinationConflictsByNumberOfAgentsExperiment import run_experiment, \
        run_experiments_to_generate_main_data_file, generate_conflict_probability_by_number_of_agents_data, \
        generate_conflict_probability_by_number_of_agents_visualization, generate_vertex_conflict_heatmap_data, \
        generate_vertex_conflict_heatmap_visualization, generate_swapping_conflict_heatmap_data, \
        generate_swapping_conflict_heatmap_visualization, generate_plan_heatmap_data, \
        generate_plan_heatmap_visualization, generate_metro_map_visualization
else:
    from ConflictsByNumberOfAgentsExperiment import run_experiment, \
        run_experiments_to_generate_main_data_file, generate_conflict_probability_by_number_of_agents_data, \
        generate_conflict_probability_by_number_of_agents_visualization, generate_vertex_conflict_heatmap_data, \
        generate_vertex_conflict_heatmap_visualization, generate_swapping_conflict_heatmap_data, \
        generate_swapping_conflict_heatmap_visualization, generate_plan_heatmap_data, \
        generate_plan_heatmap_visualization, generate_metro_map_visualization


WAREHOUSE_TYPES = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
HUGE_WAREHOUSE_IDS = [201, 202, 203, 204, 205, 206, 207]
VISUALIZE_RESULT = True
EXPORT_RESULT_TO_CSV = False


def generate_example_template(warehouse_id):
    warehouse = generate_warehouse(warehouse_id)
    algorithm_name = "BFS"

    # routing_requests, plan, vertex_conflicts, swapping_conflicts = run_experiment(warehouse, 10)
    plan, running_time, routing_requests_in_tuples_format = generate_example(warehouse, algorithm_name, [(0, 0)])

    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = True
        # visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title)

        visualization_type = "image"
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name,
                       running_time)


def generate_database(warehouse_id, max_number_of_agents, number_of_agents_incrementation_step=1,
                      number_of_samples=1000):
    warehouse = generate_warehouse(warehouse_id)
    initialize_database_preliminary_files(warehouse)

    print("***")
    print("running experiments")
    for i in range(1, max_number_of_agents + 1, number_of_agents_incrementation_step):
        run_experiments_to_generate_main_data_file(warehouse, i, number_of_samples)
        print(f"experiment {i} complete")
    print("***")
    print("Done")


def generate_conflict_probability_by_number_of_agents_scatter_plot(warehouse_id):
    print("***")
    print("Generating conflict probability by number of agents scatter plot")
    generate_conflict_probability_by_number_of_agents_data(warehouse_id)
    generate_conflict_probability_by_number_of_agents_visualization(warehouse_id)
    print("***")
    print("Done")


def generate_vertex_conflict_heatmap(warehouse_id):
    print("***")
    print("Generating vertex conflict heatmap")
    warehouse = generate_warehouse(warehouse_id, False)
    generate_vertex_conflict_heatmap_data(warehouse)
    generate_vertex_conflict_heatmap_visualization(warehouse_id)
    generate_vertex_conflict_heatmap_visualization(warehouse_id, log_scale=True)
    print("***")
    print("Done")


def generate_swapping_conflict_heatmap(warehouse_id):
    print("***")
    print("Generating swapping conflict heatmap")
    warehouse = generate_warehouse(warehouse_id, False)
    generate_swapping_conflict_heatmap_data(warehouse)
    generate_swapping_conflict_heatmap_visualization(warehouse_id)
    generate_swapping_conflict_heatmap_visualization(warehouse_id, log_scale=True)
    print("***")
    print("Done")


def generate_plan_heatmap(warehouse_id):
    print("***")
    print("Generating plan heatmap")
    warehouse = generate_warehouse(warehouse_id, False)
    generate_plan_heatmap_data(warehouse)
    generate_plan_heatmap_visualization(warehouse_id)
    generate_plan_heatmap_visualization(warehouse_id, log_scale=True)
    print("***")
    print("Done")


def generate_metro_map(warehouse_id):
    print("***")
    print("Generating metro map")
    generate_metro_map_visualization(warehouse_id)
    print("***")
    print("Done")



def main():
    """
    Choose a warehouse_id from HUGE_WAREHOUSE_IDS, and run the following code to generate the visualization for it.
    """
    warehouse_id = HUGE_WAREHOUSE_IDS[6]

    #generate_database(warehouse_id, 400, 20, 100)
    generate_conflict_probability_by_number_of_agents_scatter_plot(warehouse_id)
    generate_vertex_conflict_heatmap(warehouse_id)
    generate_swapping_conflict_heatmap(warehouse_id)
    generate_plan_heatmap(warehouse_id)
    # generate_metro_map(warehouse_id)


if __name__ == "__main__":
    main()

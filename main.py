from EnvironmentUtils import generate_warehouse
from ExampleGeneration import generate_example
from Visualization import show_plan_as_animation, show_plan_as_image

RANDOM_SCHEDULING_ENABLED = False


def main():
    """
    Supported values for algorithm_name: [BFS, RND, LNS_RND, ROR, k-ROR, IPWS, k-IPWS, MPR, k-MPR, MPR_WS, k-MPR_WS]
    - check generate_example() in ExampleGeneration.py to see which algorithm is referred to by each abbr.
    """

    warehouse_types = {"first paper": 1, "toy": 2, "small structured": 3, "small empty single origin": 4}
    warehouse = generate_warehouse(warehouse_types["small structured"])

    algorithm_name = "MPR"
    plan, running_time = generate_example(warehouse, algorithm_name)

    title = "Visualization title"
    export_visualuzation = False

    show_plan_as_animation(warehouse, plan, running_time, algorithm_name, title, export_visualuzation)
    # show_plan_as_image(warehouse, plan, running_time, algorithm_name, title, export_visualuzation)

    # TODO: export_plan_to_csv(plan, running_time, algorithm_name) - @NimrodMarom


if __name__ == "__main__":
    main()

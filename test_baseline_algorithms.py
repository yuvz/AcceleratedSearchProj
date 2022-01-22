from ExampleGeneration import generate_example, WAVES_PER_WAREHOUSE
from EnvironmentUtils import generate_warehouse
from main import WAREHOUSE_TYPES, VISUALIZE_RESULT
from Visualization import visualize_plan


def test_baseline_algorithm_sanity(warehouse, plan):
    vertexes_plan = []
    for route in plan:
        vertexes_route = [warehouse.vertices[coordinates[0]][coordinates[1]] for coordinates in route]
        vertexes_plan.append(vertexes_route)
    for i, route in enumerate(vertexes_plan):
        if not route:
            raise Exception(f"Route number {i} is empty!")
        if route[0] not in warehouse.sources:
            raise Exception(f"Route number {i} does not start at a source vertex!")
        if route[len(route)-1] not in warehouse.destinations:
            raise Exception(f"Route number {i} does not end at a destination vertex!")
        j = 1
        # The robot can wait at the source.
        while j < len(route):
            if route[j] != route[j-1]:
                break
            j += 1
        while j < len(route):
            if route[j] not in route[j-1].neighbors:
                raise Exception(f"vertex number {j} in route number {i} does not a legal neighbor of the previous vertex!")
            if route[j] in warehouse.destinations:
                break
            j += 1
    print("sanity test passed!!")


def remove_sources_and_destinationes(vertexes_list, warehouse):
    coordinates_to_remove = []
    for coordinates in vertexes_list:
        vertex_node = warehouse.vertices[coordinates[0]][coordinates[1]]
        if vertex_node in warehouse.sources or vertex_node in warehouse.destinations:
            coordinates_to_remove.append(coordinates)
    for coordinates in coordinates_to_remove:
        vertexes_list.remove(coordinates)


def test_vertex_conflict(warehouse, plan):
    max_route_len = max([len(route) for route in plan])
    for i in range(1, max_route_len):
        vertexes_at_time_i_from_all_routs = [route[i] for route in plan if i < len(route)]
        remove_sources_and_destinationes(vertexes_at_time_i_from_all_routs, warehouse)
        after_remove_len = len(vertexes_at_time_i_from_all_routs)
        if after_remove_len < 2:
            continue
        contains_vertex_conflict = len(set(vertexes_at_time_i_from_all_routs)) != after_remove_len
        if contains_vertex_conflict:
            raise Exception(f"There is a vertex conflict at time {i}")
    print("vertex conflict test passed!!!")



if __name__ == "__main__":
    warehouse = generate_warehouse(WAREHOUSE_TYPES["small structured"])
    algorithm_name = "LNS_RND"
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name)
    # print(plan)
    test_baseline_algorithm_sanity(warehouse, plan)
    # plan = [[(9, 0), (8, 0), (7, 0), (7, 1), (7, 2), (6, 2), (6, 3), (6, 4), (5, 4), (4, 4), (3, 4), (2, 4), (1, 4), (1, 5), (0, 5)],
    #         [(9, 3), (8, 3), (7, 3), (6, 3), (6, 2), (5, 2), (4, 2), (4, 1), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0)],
    #         [(9, 6), (8, 6), (7, 6), (6, 6), (5, 6), (4, 6), (3, 6), (2, 6), (2, 5), (1, 5), (0, 5)]]
    test_vertex_conflict(warehouse, plan)
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)

    warehouse = generate_warehouse(WAREHOUSE_TYPES["small structured"])
    algorithm_name = "RND"
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name)
    test_baseline_algorithm_sanity(warehouse, plan)
    # for route in plan:
    #     print(route)
    test_vertex_conflict(warehouse, plan)
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)

    warehouse = generate_warehouse(WAREHOUSE_TYPES["toy"])
    algorithm_name = "CBS"
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name)
    test_baseline_algorithm_sanity(warehouse, plan)
    test_vertex_conflict(warehouse, plan)
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)

    warehouse = generate_warehouse(WAREHOUSE_TYPES["toy"])
    algorithm_name = "RHCR"
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name, routing_requests_in_tuples_format=None,window=4, time_to_plan=3)
    test_baseline_algorithm_sanity(warehouse, plan)
    test_vertex_conflict(warehouse, plan)
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)


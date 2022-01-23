from ExampleGeneration import generate_example, WAVES_PER_WAREHOUSE
from EnvironmentUtils import generate_warehouse, count_plan_conflicts
from main import WAREHOUSE_TYPES, VISUALIZE_RESULT
from Visualization import visualize_plan


def test_baseline_algorithm_sanity(warehouse, plan):
    vertexes_plan = []
    for route in plan:
        vertexes_route = [warehouse.vertices[coordinates[0]][coordinates[1]] for coordinates in route]
        vertexes_plan.append(vertexes_route)
    for i, route in enumerate(vertexes_plan):
        if not route:
            print(f"ERROR: Route number {i} is empty!")
            return
        if route[0] not in warehouse.sources:
            print(f"ERROR: Route number {i} does not start at a source vertex!")
            return
        if route[len(route)-1] not in warehouse.destinations:
            print(f"ERROR: Route number {i} does not end at a destination vertex!")
            return
        j = 1
        # The robot can wait at the source.
        while j < len(route):
            if route[j] != route[j-1]:
                break
            j += 1
        while j < len(route):
            if route[j] not in route[j-1].neighbors:
                print(f"ERROR: vertex number {j} in route number {i} does not a legal neighbor of the previous vertex!")
                return
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
            print(f"ERROR: There is a vertex conflict at time {i}")
            return
    print("vertex conflict test passed!!!")


def test_plan_conflicts(plan):
    vertex_conflicts, swapping_conflicts = count_plan_conflicts(plan)
    if vertex_conflicts > 0 and swapping_conflicts > 0:
        print(f"ERROR: There is {vertex_conflicts} vertex conflicts and {swapping_conflicts} swapping conflicts!")
        return
    elif vertex_conflicts > 0:
        print(f"ERROR: There is {vertex_conflicts} vertex conflicts!")
        return
    elif swapping_conflicts > 0:
        print(f"ERROR: There is {swapping_conflicts} swapping conflicts!")
        return
    elif vertex_conflicts == 0 and swapping_conflicts == 0:
        print("test plan conflicts passed!!!!")
    else:
        print("ERROR: Unexpected results!")


if __name__ == "__main__":
    warehouse = generate_warehouse(WAREHOUSE_TYPES["small structured"])
    algorithm_name = "RND"
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name)
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    test_baseline_algorithm_sanity(warehouse, plan)
    test_vertex_conflict(warehouse, plan)
    test_plan_conflicts(plan)
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)

    warehouse = generate_warehouse(WAREHOUSE_TYPES["small structured"])
    algorithm_name = "LNS_RND"
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name)
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    test_baseline_algorithm_sanity(warehouse, plan)
    test_vertex_conflict(warehouse, plan)
    test_plan_conflicts(plan)
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)

    warehouse = generate_warehouse(WAREHOUSE_TYPES["toy"])
    algorithm_name = "CBS"
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name)
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    test_baseline_algorithm_sanity(warehouse, plan)
    test_vertex_conflict(warehouse, plan)
    test_plan_conflicts(plan)
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)

    warehouse = generate_warehouse(WAREHOUSE_TYPES["toy"])
    algorithm_name = "RHCR"
    plan, running_time, routing_requests = generate_example(warehouse, algorithm_name, routing_requests_in_tuples_format=None,window=4, time_to_plan=3)
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    test_baseline_algorithm_sanity(warehouse, plan)
    test_vertex_conflict(warehouse, plan)
    test_plan_conflicts(plan)
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    print("*********************************************************************************************************")
    if VISUALIZE_RESULT:
        visualization_type = "animation"
        title = ""
        is_export_visualization = False
        visualize_plan(warehouse, plan, visualization_type, is_export_visualization, title, algorithm_name, running_time)


# plan = [[(9, 0), (8, 0), (7, 0), (7, 1), (7, 2), (6, 2), (6, 3), (6, 4), (5, 4), (4, 4), (3, 4), (2, 4), (1, 4), (1, 5), (0, 5)],
#         [(9, 3), (8, 3), (7, 3), (6, 3), (6, 2), (5, 2), (4, 2), (4, 1), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0)],
#         [(9, 6), (8, 6), (7, 6), (6, 6), (5, 6), (4, 6), (3, 6), (2, 6), (2, 5), (1, 5), (0, 5)]]

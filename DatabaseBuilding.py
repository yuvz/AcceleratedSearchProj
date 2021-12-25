from typing import List, Tuple

from RouteGeneration import generate_midpoints_restricted_plan


# TODO: @NimrodMarom
def export_routes_to_csv(algorithm_name, source_id, destination_id, routes):
    """
    Generates a .csv file using the above input
    """
    pass


def create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination):
    return generate_midpoints_restricted_plan(warehouse, source, destination, True)


def create_tagged_routes_by_MPR_WS(warehouse):
    tagged_routes: List[Tuple[Tuple[int, int], List]] = []
    for i, source in enumerate(warehouse.sources):
        for j, destination in enumerate(warehouse.destinations):
            routes = create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination)
            tagged_routes.append(((i, j), routes))

    return tagged_routes

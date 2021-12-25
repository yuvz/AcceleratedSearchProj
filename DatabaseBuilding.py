from typing import List, Tuple, Dict
import csv
from RouteGeneration import generate_midpoints_restricted_plan

PATH_GENERATING_ALGORITHMS = ["ROR", "K-ROR", "IPWS", "K-IPWS", "MPR", "K-MPR", "MPR_WS"]

def import_csv_to_routes(csv_file: str) -> List: 
    """ 

    Args:
        csv_file (str): the name of the csv file

    Returns:
        [List]: A list of all the routes from the csv_file
    """
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        routes = list(reader)
        routes = routes[1:]
        routes = [route[3:] for route in routes]
        return routes

def create_header_routes_csv(routes, warehouse) -> List:
    """ 

    Args:
        routes (List): list of all the rotes(lists)

    Returns:
        List: headers of the table
    """
    columns_length = warehouse.length + warehouse.width
    field_names = ['Algorithm Name', 'Source Id', 'Destination Id']
    for i in range(columns_length):
        field_name = 'Time = {}'.format(i + 1)
        field_names.append(field_name)
    field_names.append('Grade')
    return field_names

def create_line_routes_csv(algorithm_name: str, source_id, destination_id, field_names : List, route) -> Dict:
    """

    Args:
        algorithm_name (str): Name of the algorithm  
        source_id ([int]): Id of the vertex source
        destination_id ([int]): Id of the vertex destination
        field_names (List): List of strings - header of the line in a table
        rout (List): route of touples from source to destination

    Returns:
        Dict: [Table line of {header_type_1:value_1, ... header_type_n:value_n}]
    """
    line = {}
    for i in field_names:
        line[i] = None
    line['Algorithm Name'] = algorithm_name
    line['Source Id'] = source_id
    line['Destination Id'] = destination_id
    for i in range(len(route)):
        line[field_names[i + 3]] = route[i]
    return line

def export_routes_to_csv(algorithm_name, source_id, destination_id, routes, warehouse):
    """    Generates a .csv file using the above input

    Args:
        algorithm_name (str): name of the algorithm
        source_id (int): id of source vertex
        destination_id (int): id of destination vertex
        routes (list): list of all the routes(lists) available
    """
    field_names = create_header_routes_csv(routes, warehouse)
    file_name = 'routes_from_{}_to_{}.csv'.format(source_id,destination_id)
    with open(file_name, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        
        for i in range(len(routes)):
            line = create_line_routes_csv(algorithm_name, source_id, destination_id, field_names, routes[i])
            writer.writerow(line)

def create_header_warehouse_csv(warehouse) -> List:
    """ 

    Args:
        routes (List): list of all the rotes(lists)

    Returns:
        List: headers of the table
    """
    field_names = ['Warehouse Id','Width', 'Length', 'Number Of Sources', 'Number Of Destinations', 'Static Obstacle Width', 'Static Obstacle Length']    
    for i in range(len(warehouse.sources)):
        field_name = 'Source {}'.format(i + 1)
        field_names.append(field_name)
    for i in range(len(warehouse.destinations)):
        field_name = 'Destination {}'.format(i + 1)
        field_names.append(field_name)
    for i in range(len(warehouse.static_obstacle_coordinates_split_by_obstacle)):
        field_name = 'Obstacle {}'.format(i + 1)
        field_names.append(field_name)
                
    return field_names

def create_line_warehouse_csv(warehouse) -> Dict:
    line = {}
    for i in range(len(warehouse.sources)):
        header = 'Source {}'.format(i + 1)
        line[header] = warehouse.sources[i].coordinates
    for i in range(len(warehouse.destinations)):
        header = 'Destination {}'.format(i + 1)
        line[header] = warehouse.destinations[i].coordinates
    for i in range(len(warehouse.static_obstacle_coordinates_split_by_obstacle)):
        header = 'Obstacle {}'.format(i + 1)
        line[header] = warehouse.static_obstacle_coordinates_split_by_obstacle[i]
    line['Warehouse Id'] = warehouse.warehouse_id
    line['Width'] = warehouse.width
    line['Length'] = warehouse.length
    line['Number Of Sources'] = warehouse.number_of_sources
    line['Number Of Destinations'] = warehouse.number_of_destinations
    line['Static Obstacle Width'] = warehouse.static_obstacle_width
    line['Static Obstacle Length'] = warehouse.static_obstacle_length
    return line

def export_warehouse_to_csv(warehouse) :
    """ Generates a .csv file using the above input

    Args:
        warehouse 
    """
    field_names = create_header_warehouse_csv(warehouse)
    file_name = 'warehouse_{}.csv'.format(warehouse.warehouse_id)
    with open(file_name, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        
        line = create_line_warehouse_csv(warehouse)
        
        writer.writerow(line)

def create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination):
    return generate_midpoints_restricted_plan(warehouse, source, destination, True)


def create_tagged_routes_by_MPR_WS(warehouse):
    tagged_routes: List[Tuple[Tuple[int, int], List]] = []
    for i, source in enumerate(warehouse.sources):
        for j, destination in enumerate(warehouse.destinations):
            routes = create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination)
            tagged_routes.append(((i, j), routes))

    return tagged_routes

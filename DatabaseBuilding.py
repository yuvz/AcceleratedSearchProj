import os
from typing import List, Tuple, Dict
import csv

from EnvironmentUtils import get_source_id_from_route, get_destination_id_from_route


def import_plan_from_csv(csv_file: str) -> List:
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
        warehouse (Warehouse)

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


def create_line_routes_csv(algorithm_name: str, source_id, destination_id, field_names: List, route) -> Dict:
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


def create_header_warehouse_csv(warehouse) -> List:
    """ 

    Args:
        warehouse (Warehouse)

    Returns:
        List: headers of the table
    """
    field_names = ['Warehouse Id', 'Width', 'Length', 'Number Of Sources', 'Number Of Destinations',
                   'Static Obstacle Width', 'Static Obstacle Length']
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


def export_warehouse_information_to_csv(warehouse):
    """ Generates a .csv file using the above input

    Args:
        warehouse 
    """
    file_name = 'warehouse_{}/warehouse_{}_information.csv'.format(warehouse.warehouse_id, warehouse.warehouse_id)
    with open(file_name, 'w', newline='') as f:
        field_names = create_header_warehouse_csv(warehouse)
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()

        line = create_line_warehouse_csv(warehouse)

        writer.writerow(line)


def export_plan_to_csv(algorithm_name, plan, warehouse):
    """    Generates a .csv file using the above input

    Args:
        algorithm_name (str): name of the algorithm
        plan (list): list of all the routes(lists) available
        warehouse (Warehouse)
    """
    target_dir = "./warehouse_{}".format(warehouse.warehouse_id)
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)
        export_warehouse_information_to_csv(warehouse)

    for route in plan:
        source_id = get_source_id_from_route(warehouse, route)
        destination_id = get_destination_id_from_route(warehouse, route)

        file_name = 'warehouse_{}/routes_from_{}_to_{}.csv'.format(warehouse.warehouse_id, source_id, destination_id)
        with open(file_name, 'a', newline='') as f:
            field_names = create_header_routes_csv(plan, warehouse)
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()

            line = create_line_routes_csv(algorithm_name, source_id, destination_id, field_names, route)
            writer.writerow(line)

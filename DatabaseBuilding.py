from typing import List, Tuple, Dict
import csv
from RouteGeneration import generate_midpoints_restricted_plan
from Warehouse import Warehouse
import random
import os

from EnvironmentUtils import get_source_id_from_route, get_destination_id_from_route

def create_length(rows: List) -> int:
    """

    Args:
        rows (List): list of dictyonarys - each row is a dictionary of source to target route

    Returns:
        int: sum of total length of the routes
    """
    length = 0
    for row in rows:
        row['Algorithm Name'] = None
        row['Source Id'] = None
        row['Destination Id'] = None
        row = dict((k,v) for k, v in row.items() if v is not None)
        lenth = length + len(row)
    return length

def create_row_from_tupple(source: int, target: int) -> Dict : 
    """ Generate a path from source to target from existing csv file    

    Args:
        source (int): Source Id
        target (int): Target Id

    Returns:
        Dict: Returns random route from source to target
    """

    file_name = 'routes_from_{}_to_{}.csv'.format(source, target)
    data = import_csv_to_routes(file_name)
    row = random.randrage(0, len(data))
    return data[row]
    
def export_all_routes_to_csv(warehouse: Warehouse, source_dest_list: List) -> None:
    """ Creates a .csv file of routes for all the souce,dest tupples that were given

    Args:
        source_dest_list (List): List of tupples of wanted (source, dest) routes
    """

    field_names = create_header_routes_csv(warehouse)
    file_name = 'routes.csv'
    with open(file_name, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        rows = []
        for tupple in source_dest_list:
            row = create_row_from_tupple(source_dest_list[0], source_dest_list[1])
            rows.append(row)
        writer.writerows(rows)
        total_length = create_length(rows)
        #number_of_clashes = create_number_of_clashes(rows)


def import_csv_to_routes(csv_file: str) -> List: 
    """ 

    Args:
        csv_file (str): The name of the csv file

    Returns:
        [List]: A list of all the routes from the csv_file
    """
    with open(csv_file, newline='') as f:
        reader = csv.DictReader()
        routes = list(reader)
        routes = routes[1:]
        routes = [route[3:] for route in routes]
        return routes

def create_header_routes_csv(warehouse: Warehouse) -> List:
    """ 

    Args:
        routes (List): List of all the rotes(lists)

    Returns:
        List: Headers of the table
    """
    columns_length = warehouse.length + warehouse.width
    field_names = ['Algorithm Name', 'Source Id', 'Destination Id']
    for i in range(columns_length):
        field_name = 'Time = {}'.format(i + 1)
        field_names.append(field_name)
    field_names.append('Grade')
    return field_names

def create_row_routes_csv(algorithm_name: str, source_id: int, destination_id: int, field_names : List, route: List) -> Dict:
    """

    Args:
        algorithm_name (str): Name of the algorithm  
        source_id ([int]): Id of the vertex source
        destination_id ([int]): Id of the vertex destination
        field_names (List): List of strings - header of the row in a table
        rout (List): route of touples from source to destination

    Returns:
        Dict: [Table row of {header_type_1:value_1, ... header_type_n:value_n}]
    """
    row = {}
    for i in field_names:
        row[i] = None
    row['Algorithm Name'] = algorithm_name
    row['Source Id'] = source_id
    row['Destination Id'] = destination_id
    for i in range(len(route)):
        row[field_names[i + 3]] = route[i]
    return row

def export_routes_to_csv(algorithm_name: str, source_id: int, destination_id: int, routes: List, warehouse: Warehouse):
    """    Generates a .csv file using the above input

    Args:
        algorithm_name (str): Name of the algorithm
        source_id (int): Id of source vertex
        destination_id (int): Id of destination vertex
        routes (list): List of all the routes(lists) available
    """
    field_names = create_header_routes_csv(warehouse)
    file_name = 'routes_from_{}_to_{}.csv'.format(source_id,destination_id)
    file_exists = os.path.isfile(file_name)
    with open(file_name, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        if not file_exists:
            writer.writeheader()
        rows = []
        for i in range(len(routes)):
            row = create_row_routes_csv(algorithm_name, source_id, destination_id, field_names, routes[i])
            rows.append(row)
        writer.writerows(rows)

def create_header_warehouse_csv(warehouse: Warehouse) -> List:
    """ 

    Args:
        warehouse (Warehouse): 

    Returns:
        List: Headers of the table
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

def create_row_warehouse_csv(warehouse: Warehouse) -> Dict:
    """

    Args:
        warehouse (Warehouse): 

    Returns:
        Dict: A row for the warehouse csv with the values for the table
    """
    row = {}
    for i in range(len(warehouse.sources)):
        header = 'Source {}'.format(i + 1)
        row[header] = warehouse.sources[i].coordinates
    for i in range(len(warehouse.destinations)):
        header = 'Destination {}'.format(i + 1)
        row[header] = warehouse.destinations[i].coordinates
    for i in range(len(warehouse.static_obstacle_coordinates_split_by_obstacle)):
        header = 'Obstacle {}'.format(i + 1)
        row[header] = warehouse.static_obstacle_coordinates_split_by_obstacle[i]
    row['Warehouse Id'] = warehouse.warehouse_id
    row['Width'] = warehouse.width
    row['Length'] = warehouse.length
    row['Number Of Sources'] = warehouse.number_of_sources
    row['Number Of Destinations'] = warehouse.number_of_destinations
    row['Static Obstacle Width'] = warehouse.static_obstacle_width
    row['Static Obstacle Length'] = warehouse.static_obstacle_length
    return row

def export_warehouse_to_csv(warehouse: Warehouse) :
    """ Generates a .csv file using the above input

    Args:
        warehouse (Warehouse)
    """
    file_name = 'warehouse_{}.csv'.format(warehouse.warehouse_id)
    with open(file_name, 'w', newline='') as f:
        field_names = create_header_warehouse_csv(warehouse)
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        
        row = create_row_warehouse_csv(warehouse)
        writer.writerow(row)


def create_tagged_routes_by_MPR_WS(warehouse: Warehouse):
    tagged_routes: List[Tuple[Tuple[int, int], List]] = []
    for i, source in enumerate(warehouse.sources):
        for j, destination in enumerate(warehouse.destinations):
            routes = create_routes_from_source_to_destination_by_MPR_WS(warehouse, source, destination)
            tagged_routes.append(((i, j), routes))


def export_plan_to_csv(algorithm_name, plan, warehouse):
    """   Generates a .csv file using the above input

    Args:
        algorithm_name (str): name of the algorithm
        plan (list): list of all the routes(lists) available
        warehouse (Warehouse)
    """
    for route in plan:
        source_id = get_source_id_from_route(warehouse, route)
        destination_id = get_destination_id_from_route(warehouse, route)

        # TODO: create warehouse_{} directory if doesn't exist
        warehouse_id = warehouse.warehouse_id
        file_name = '/warehouse_{}/routes_from_{}_to_{}.csv'.format(warehouse_id, source_id, destination_id)
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'a', newline='') as f:
            field_names = create_header_routes_csv(plan, warehouse)
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()

            row = create_row_routes_csv(algorithm_name, source_id, destination_id, field_names, route)
            writer.writerow(row)

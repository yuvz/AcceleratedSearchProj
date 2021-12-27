import os
from typing import List, Tuple, Dict
import csv
import Warehouse
import random
import math
from EnvironmentUtils import get_source_id_from_route, get_destination_id_from_route
import operator as op
from functools import reduce

from EnvironmentUtils import get_source_id_from_route, get_destination_id_from_route


def nCk(n, r):
    """ claculatimg combinatorics: n chose r
    """
    if n == 0:
        return 0

    r = min(r, n - r)
    numer = reduce(op.mul, range(n, n - r, -1), 1)
    denom = reduce(op.mul, range(1, r + 1), 1)
    return numer // denom


def create_number_of_collision(rows: List, field_names: List, column_length: int) -> int:
    """ calculates the total number of collision

    Args:
        rows (List): List of all the routes
        column_length (int): max length of columns
    Returns:
        int: number of collision  (1: switching places; 2: standing in same place in same time)
    """
    # column length = n; number of rows = m

    same_place_count = 0
    same_place_count_time_i = 0
    # checking collisions inside columns - O(m^2 * n)
    for time_i in range(column_length):
        same_place_count_time_i = 0
        for row in range(len(rows)):
            if rows[row][field_names[time_i]] == '' or time_i in [0, 1, 2]:
                continue
            row_below = row + 1
            while row_below < len(rows):
                if rows[row_below][field_names[time_i]] == '':
                    row_below = row_below + 1
                    continue
                if rows[row][field_names[time_i]] == rows[row_below][field_names[time_i]]:
                    same_place_count_time_i = same_place_count_time_i + 1
                row_below = row_below + 1

        same_place_count = same_place_count + nCk(same_place_count_time_i, 2)  # n chose k

    # checking collisions with changing places - O(n^2 * m)
    changing_places_count = 0
    for row in range(len(rows) - 1):
        for time_i in range(column_length - 1):
            if rows[row][field_names[time_i]] == '' or \
                    rows[row + 1][field_names[time_i]] == '' or time_i in [0, 1, 2]:
                continue
            row_below = row + 1
            while row_below < len(rows):
                if rows[row_below][field_names[time_i]] == '' or \
                        rows[row_below][field_names[time_i + 1]] == '':
                    row_below = row_below + 1
                    continue
                if rows[row][field_names[time_i]] == rows[row_below][field_names[time_i + 1]] and \
                        rows[row][field_names[time_i + 1]] == rows[row_below][field_names[time_i]]:
                    changing_places_count = changing_places_count + 1
                row_below = row_below + 1

    return same_place_count + changing_places_count


def create_length(rows: List) -> int:
    """
    Args:
        rows (List): list of dictyonarys - each row is a dictionary of source to target route

    Returns:
        int: sum of total length of the routes
    """
    length = 0
    for row in rows:
        row['Algorithm Name'] = ''
        row['Source Id'] = ''
        row['Destination Id'] = ''
        row = dict((k, v) for k, v in row.items() if v != '')
        length = length + len(row)
    return length


def create_row_from_tupple(source: int, target: int, field_names: List, warehouse: Warehouse) -> Dict:
    """ Generate a path from source to target from existing csv file

    Args:
        source (int): Source Id
        target (int): Target Id
        field_names (List) : a list of the headers
        warehouse (Warehouse)
    Returns:
        Dict: Returns random route from source to target
    """

    file_name = './csv_files/warehouse_{}/routes/routes_from_{}_to_{}.csv'.format(warehouse.warehouse_id, source,
                                                                                  target)
    file_exists = os.path.isfile(file_name)
    if not file_exists:
        return None
    data = import_plan_from_csv(file_name, field_names)
    random_route_number = random.randint(0, (len(data) - 1))
    return data[random_route_number]


def export_all_routes_to_csv(warehouse: Warehouse, source_dest_list: List) -> None:
    """ Creates a .csv file of routes for all the souce,dest tupples that were given

    Args:
        source_dest_list (List): List of tupples of wanted (source, dest) routes
    """

    field_names = create_header_routes_csv(warehouse)
    file_name = './csv_files/warehouse_{}/all_chosen_routes.csv'.format(warehouse.warehouse_id)
    file_exists = os.path.isfile(file_name)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        rows = []
        for tupple in source_dest_list:
            row = create_row_from_tupple(tupple[0], tupple[1], field_names, warehouse)
            rows.append(row)
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writerows(rows)
        total_length = create_length(rows)
        columns_length = warehouse.length + warehouse.width
        number_of_collisions = create_number_of_collision(rows, field_names, columns_length)
        writer = csv.writer(f)
        total_length_str = 'Total Lenth:' + str(total_length)
        number_of_collisions_Str = 'Total collisions:' + str(number_of_collisions)
        calc_values = [total_length_str, number_of_collisions_Str]
        writer.writerow(calc_values)


def import_plan_from_csv(csv_file: str, field_names: List = None) -> List:
    """ 

    Args:
        csv_file (str): The name of the csv file

    Returns:
        [List]: A list of all the routes from the csv_file
    """
    # check first if file exists
    file_exists = os.path.isfile(csv_file)
    if not file_exists:
        return []
    with open(csv_file, newline='') as f:
        if field_names is None:
            reader = csv.reader(f)
            routes = list(reader)
            routes = routes[1:]
            routes = [route[3:] for route in routes]
            routes = [[tupple for tupple in row if tupple] for row in routes]  # removing empty cells
            routes = [[eval(tupple) for tupple in row if tupple] for row in routes]  # converting string to Tupple
        else:
            with open(csv_file, newline='') as f:
                reader = csv.DictReader(f)
                routes = []
                for row in reader:
                    dict_row = {}
                    for field_name in field_names:
                        dict_row[field_name] = row[field_name]
                    routes.append(dict_row)
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
    return field_names


def create_row_routes_csv(algorithm_name: str, source_id: int, destination_id: int, field_names: List,
                          route: List) -> Dict:
    """

    Args:
        algorithm_name (str): Name of the algorithm  
        source_id ([int]): Id of the vertex source
        destination_id ([int]): Id of the vertex destination
        field_names (List): List of strings - header of the row in a table
        route (List): route of touples from source to destination

    Returns:
        Dict: [Table row of {header_type_1:value_1, ... header_type_n:value_n}]
    """
    row = {}
    for field_name in field_names:
        row[field_name] = None
    row['Algorithm Name'] = algorithm_name
    row['Source Id'] = source_id
    row['Destination Id'] = destination_id
    for i in range(len(route)):
        row[field_names[i + 3]] = route[i]
    return row


# def export_routes_source_to_dest_to_csv(algorithm_name: str, source_id: int, destination_id: int, routes: List,
#                                         warehouse: Warehouse):
#     """    Generates a .csv file using the above input
#
#     Args:
#         algorithm_name (str): Name of the algorithm
#         source_id (int): Id of source vertex
#         destination_id (int): Id of destination vertex
#         routes (list): List of all the routes(lists) available
#     """
#     field_names = create_header_routes_csv(warehouse)
#
#     file_name = './csv_files/warehouse_{}/routes/routes_from_{}_to_{}.csv'.format(warehouse.warehouse_id, source_id,
#                                                                                   destination_id)
#     file_exists = os.path.isfile(file_name)
#     os.makedirs(os.path.dirname(file_name), exist_ok=True)
#
#     file_exists = os.path.isfile(file_name)
#     with open(file_name, 'a', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=field_names)
#         if not file_exists:
#             writer.writeheader()
#         rows = []
#         for i in range(len(routes)):
#             row = create_row_routes_csv(algorithm_name, source_id, destination_id, field_names, routes[i])
#             rows.append(row)
#         writer.writerows(rows)


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


def export_warehouse_information_to_csv(warehouse: Warehouse):
    """ Generates a .csv file using the above input

    Args:
        warehouse (Warehouse)
    """
    file_name = './csv_files/warehouse_{}/warehouse_{}_information.csv'.format(warehouse.warehouse_id,
                                                                               warehouse.warehouse_id)
    file_exists = os.path.isfile(file_name)

    with open(file_name, 'w', newline='') as f:
        field_names = create_header_warehouse_csv(warehouse)
        writer = csv.DictWriter(f, fieldnames=field_names)
        if not file_exists:
            writer.writeheader()

        row = create_row_warehouse_csv(warehouse)
        writer.writerow(row)


def export_plan_to_csv(algorithm_name, plan, warehouse):
    """   Generates a .csv file using the above input

    Args:
        algorithm_name (str): name of the algorithm
        plan (list): list of all the routes(lists) available
        warehouse (Warehouse)
    """
    target_dir = "./csv_files/warehouse_{}/routes/".format(warehouse.warehouse_id)

    if not os.path.isdir(target_dir):
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        export_warehouse_information_to_csv(warehouse)

    for route in plan:
        source_id = get_source_id_from_route(warehouse, route)
        destination_id = get_destination_id_from_route(warehouse, route)

        warehouse_id = warehouse.warehouse_id
        file_name = './csv_files/warehouse_{}/routes/routes_from_{}_to_{}.csv'.format(warehouse_id, source_id,
                                                                                      destination_id)
        file_exists = os.path.isfile(file_name)

        with open(file_name, 'a', newline='') as f:
            field_names = create_header_routes_csv(warehouse)
            writer = csv.DictWriter(f, fieldnames=field_names)
            if not file_exists:
                writer.writeheader()

            row = create_row_routes_csv(algorithm_name, source_id, destination_id, field_names, route)
            writer.writerow(row)

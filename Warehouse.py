from queue import Queue
from typing import List, Set, Tuple
import matplotlib.pyplot as plt

SOURCE_OFFSET = 3
DESTINATION_OFFSET = 5
ALLOW_DIAGONAL_MOVEMENT = False
PRIORITIZE_AGENTS_WAITING_AT_SOURCE = True

WAREHOUSE_1_WALL_CORNERS = [(21, 15), (21, 46), (21, 105), (28, 82), (45, 50), (45, 70), (45, 95), (57, 19),
                            (73, 70), (60, 115)]
WAREHOUSE_2_WALL_CORNERS = [(3, 2), (3, 5), (4, 7), (6, 5)]
WAREHOUSE_3_WALL_CORNERS = [(30, 5), (30, 15), (30, 25), (30, 35), (25, 0), (25, 10), (25, 20), (25, 30),
                            (20, 5), (20, 15), (20, 25), (20, 35), (15, 0), (15, 10), (15, 20), (15, 30),
                            (10, 5), (10, 15), (10, 25), (10, 35), (5, 0), (5, 10), (5, 20), (5, 30)]
WAREHOUSE_4_WALL_CORNERS = []
WAREHOUSE_CORNERS = [WAREHOUSE_1_WALL_CORNERS, WAREHOUSE_2_WALL_CORNERS, WAREHOUSE_3_WALL_CORNERS,
                     WAREHOUSE_4_WALL_CORNERS]


class Warehouse:
    class WarehouseNode:
        def __init__(self, coordinates, number_of_destinations):
            self.coordinates = coordinates
            self.destination_distance = [0 for _ in range(number_of_destinations)]

            self.is_static_obstacle = False
            self.source_id = -1  # not optimal solution, but simplifies implementation
            self.destination_id = -1  # not optimal solution, but simplifies implementation
            self.neighbors = set()

        def get_destination_distance(self, destination_id):
            return self.destination_distance[destination_id]

    """
         Uses a breadth first search to calculate the distances of all vertices in the warehouse from the ith 
         destination.
         This algorithm avoids static obstacles and ignores dynamic obstacles
    """

    def set_ith_destination_distances(self, i):
        destination = self.destinations[i]
        destination_coordinates = destination.coordinates
        destination_entrance = self.vertices[destination_coordinates[0] + 1][destination_coordinates[1]]

        destination.destination_distance[i] = 0
        destination_entrance.destination_distance[i] = 1

        queue = Queue()
        queue.put(destination_entrance)
        visited = set()
        visited.add(destination)
        visited.add(destination_entrance)
        while not queue.empty():
            u = queue.get()
            for v in u.neighbors:
                if v not in visited:
                    v.destination_distance[i] = u.destination_distance[i] + 1
                    visited.add(v)
                    queue.put(v)
            visited.add(u)

        for source in self.sources:
            source_coordinates = source.coordinates
            source_entrance = self.vertices[source_coordinates[0] - 1][source_coordinates[1]]
            source.destination_distance[i] = 1 + source_entrance.destination_distance[i]

    def set_destination_distances(self):
        for i in range(self.number_of_destinations):
            self.set_ith_destination_distances(i)

    def adjust_destinations_neighbors(self):
        for destination in self.destinations:
            destination_coordinates = destination.coordinates

            for neighbor in destination.neighbors:
                if (neighbor.coordinates[0] - destination_coordinates[0],
                        neighbor.coordinates[1] - destination_coordinates[1]) != (1, 0):
                    neighbor.neighbors.remove(destination)

            destination.neighbors = set()

    def adjust_sources_neighbors(self):
        for source in self.sources:
            source_coordinates = source.coordinates
            neighbors_to_remove = []

            for neighbor in source.neighbors:
                neighbor.neighbors.remove(source)

                neighbor_coordinates = neighbor.coordinates
                if (source_coordinates[0] - neighbor_coordinates[0], source_coordinates[1] - neighbor_coordinates[1]) \
                        != (1, 0):
                    neighbors_to_remove.append(neighbor)

            source.neighbors = source.neighbors.difference(neighbors_to_remove)

    def set_sources_and_destinations(self, number_of_targets, row_idx, target_array, is_destination=False):
        offset = DESTINATION_OFFSET if is_destination else SOURCE_OFFSET
        area_without_offsets = self.width - offset
        remainder_from_right_wall = area_without_offsets % number_of_targets

        first_target_position = offset
        last_target_position = self.width - remainder_from_right_wall
        distance_between_targets = int((area_without_offsets - remainder_from_right_wall) / number_of_targets)

        for i, column_idx in enumerate(range(first_target_position, last_target_position, distance_between_targets)):
            vertex = self.vertices[row_idx][column_idx]
            target_array.append(vertex)

            if is_destination:
                vertex.destination_id = i
            else:
                vertex.source_id = i

    def set_destinations(self):
        self.set_sources_and_destinations(self.number_of_destinations, 0, self.destinations, True)

    def set_sources(self):
        self.set_sources_and_destinations(self.number_of_sources, self.length - 1, self.sources)

    def is_valid_vertex(self, row_idx, column_idx):
        if (0 <= row_idx < self.length) and (0 <= column_idx < self.width):
            return not self.vertices[row_idx][column_idx].is_static_obstacle

        return False

    """
    Note:   Diagonal neighbors are valid neighbors, while static obstacles are not.
            Also, a vertex cannot be a neighbor of itself
    """

    def set_neighbors(self):
        for row in self.vertices:
            for vertex in row:
                if vertex.is_static_obstacle:
                    continue

                for i in [-1, 0, 1]:
                    row_idx = vertex.coordinates[0] + i

                    for j in [-1, 0, 1]:
                        if not ALLOW_DIAGONAL_MOVEMENT and i ** 2 + j ** 2 != 1:
                            continue

                        column_idx = vertex.coordinates[1] + j
                        if (i != 0 or j != 0) and self.is_valid_vertex(row_idx, column_idx):
                            neighbor = self.vertices[row_idx][column_idx]
                            vertex.neighbors.add(neighbor)

    """
        Sets a rectangular static obstacle with a corner at the given indices
    """

    def set_static_obstacle(self, row_idx, column_idx):
        for i in range(self.static_obstacle_length):
            obstacle_row_idx = row_idx + i

            if 0 <= obstacle_row_idx < self.length:
                for j in range(self.static_obstacle_width):
                    obstacle_column_idx = column_idx + j

                    if 0 <= obstacle_column_idx < self.width:
                        self.vertices[obstacle_row_idx][obstacle_column_idx].is_static_obstacle = True

                        # used for animations
                        if i == 0 or i == self.static_obstacle_length - 1 or j == 0 \
                                or j == self.static_obstacle_width - 1:
                            self.static_obstacle_corners.add((obstacle_row_idx, obstacle_column_idx))

    def set_static_obstacles(self):
        corners_coordinates = WAREHOUSE_CORNERS[self.warehouse_id - 1]
        for corner_coordinates in corners_coordinates:
            self.set_static_obstacle(corner_coordinates[0], corner_coordinates[1])

    def initialize_vertices(self):
        for row_idx in range(self.length):
            column = []

            for column_idx in range(self.width):
                coordinates = (row_idx, column_idx)
                new_vertex = self.WarehouseNode(coordinates, self.number_of_destinations)

                column.append(new_vertex)

            self.vertices.append(column)

    def __init__(self, warehouse_id, length, width, number_of_sources, number_of_destinations, static_obstacle_length,
                 static_obstacle_width):
        self.warehouse_id = warehouse_id
        self.length = length
        self.width = width
        self.number_of_sources = number_of_sources
        self.number_of_destinations = number_of_destinations
        self.static_obstacle_length = static_obstacle_length
        self.static_obstacle_width = static_obstacle_width

        self.vertices: List[List[Warehouse.WarehouseNode]] = []
        self.static_obstacles = set()
        self.static_obstacle_corners: Set[Tuple[int, int]] = set()
        self.sources: List[Warehouse.WarehouseNode] = []
        self.destinations: List[Warehouse.WarehouseNode] = []

        self.initialize_vertices()
        self.set_static_obstacles()
        self.set_neighbors()

        self.set_sources()
        self.set_destinations()

        self.adjust_sources_neighbors()
        self.adjust_destinations_neighbors()
        self.set_destination_distances()

    def plot_layout(self):
        fig = plt.figure()
        ax = plt.axes(xlim=(0, self.width - 1), ylim=(0, self.length - 1))
        for source in self.sources:
            plt.scatter(source.coordinates[1], source.coordinates[0], s=250, marker='v', c='#00964b')

        for obstacle in self.static_obstacle_corners:
            if self.warehouse_id == 1:
                plt.scatter(obstacle[1], obstacle[0], s=10, c='black')
            elif self.warehouse_id == 2:
                plt.scatter(obstacle[1], obstacle[0], s=50, marker='s', c='black')
            else:
                plt.scatter(obstacle[1], obstacle[0], s=10, marker='s', c='black')

        for destination in self.destinations:
            plt.scatter(destination.coordinates[1], destination.coordinates[0], s=250, marker='^', c='hotpink')

        plt.xlim(0, self.width)
        plt.ylim(0, self.length - 1)
        plt.grid()

        return fig, ax

    def show(self):
        self.plot_layout()
        plt.show()
        plt.clf()

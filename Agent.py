import numpy as np
from Warehouse import Warehouse

ALLOW_DIAGONAL_MOVEMENT = False
PRIORITIZE_AGENTS_WAITING_AT_SOURCE = True


class Agent:
    """
       Prioritize a robot blocking the destination
       Otherwise, prioritize for smaller row_idx
       Otherwise, larger destination_distance
    """

    def __init__(self, agent_id: int, source: Warehouse.WarehouseNode, destination: Warehouse.WarehouseNode):
        self.agent_id = agent_id
        self.source = source
        self.destination = destination

        self.left_source = False
        self.previous_vertex = None

    def __lt__(self, other):
        self_destination_distance = self.get_destination_distance()
        other_destination_distance = other.get_destination_distance()

        if self_destination_distance <= 0:
            return True
        if other_destination_distance <= 0:
            return False

        if self.source.coordinates[0] < other.source.coordinates[0]:
            return True
        return self_destination_distance > other_destination_distance

    # Uniquely identify an agent with its start position
    def __hash__(self):
        return int(str(self.source.coordinates[0]) + str(self.source.coordinates[1]))

    def __eq__(self, other: 'Agent'):
        return np.array_equal(self.source.coordinates, other.source.coordinates) and \
               np.array_equal(self.destination.coordinates, other.destination.coordinates)

    def __str__(self):
        return str(np.array(self.source.coordinates).tolist())

    def __repr__(self):
        return self.__str__()

    def get_destination_distance(self):
        return self.source.destination_distance[self.destination.destination_id]

    def is_at_destination(self):
        return self.get_destination_distance() == 0

    def get_source_id(self):
        return self.source.source_id

    def get_destination_id(self):
        return self.destination.destination_id

    def comparator_source_destination_id(self, other):
        if self.get_source_id() < other.get_source_id():
            return -1
        elif self.get_source_id() == other.get_source_id:
            if self.get_destination_id() < other.get_destination_id():
                return -1
            elif self.get_destination_id() == other.get_destination_id():
                return 0
            else:
                return 1
        else:
            return 1

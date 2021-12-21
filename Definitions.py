class Agent:
    """
       Prioritize a robot blocking the destination
       Otherwise, prioritize for smaller row_idx
       Otherwise, larger destination_distance
    """

    def __lt__(self, other):
        self_destination_distance = self.get_destination_distance()
        other_destination_distance = other.get_destination_distance()

        if self_destination_distance <= 0:
            return True
        if other_destination_distance <= 0:
            return False

        if self.vertex.coordinates[0] < other.vertex.coordinates[0]:
            return True
        return self_destination_distance > other_destination_distance

    def __init__(self, agent_id, vertex, destination):
        self.agent_id = agent_id
        self.vertex = vertex
        self.destination = destination

        self.left_source = False
        self.previous_vertex = None

    def get_destination_distance(self):
        return self.vertex.destination_distance[self.destination.destination_id]

    def is_at_destination(self):
        return self.get_destination_distance() == 0

    def get_source_id(self):
        return self.vertex.source_id

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

    def get_ideal_neighbor(self):
        ideal_neighbor = None
        min_destination_distance = self.get_destination_distance() + 1

        for neighbor in self.vertex.neighbors:
            neighbor_destination_distance = neighbor.get_destination_distance(self.destination.destination_id)
            if neighbor_destination_distance < min_destination_distance:
                min_destination_distance = neighbor_destination_distance
                ideal_neighbor = neighbor

        return ideal_neighbor

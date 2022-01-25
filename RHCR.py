from CBS.CBS import CBS


class RHCR:
    """
    window - the plan is free of conflicts until window
    time_to_plan - time to run CBS again
    window has to be greater than time_to_plan at least by one in this implementation.
    In this implementation of RHCR:
    RHCR run CBS in iterations. Each iteration CBS considers only the conflicts inside window.
    Then, RHCR takes only part of the solution for each route - until time_to_plan.
    Then, in the next iteration RHCR calls CBS with new sources - the vertex *after* time_to_plan.
    That is the reason the window has to be greater than time_to_plan, so there will not be conflicts.
    In conclusion, you may consider the actual part of the routs that RHCR calculates each iteration - time_to_plan + 1.
    (without the overlapping between two sequential routs' parts, each part is in size of time_to_plan.
     with the overlapping, each part is in size of time_to_plan + 1.)
    """
    def __init__(self, window, time_to_plan):
        self.window = window
        self.time_to_plan = time_to_plan

    def generate_rhcr_plan(self, warehouse, routing_requests):
        if self.window < 2 or self.time_to_plan < 1 or self.window-self.time_to_plan < 1:
            print("non valid window/time_to_plan values.")
            print("time to plan has to be at least 1.")
            print("window has to be greater than time to plan.")
            return
        plan = [[] for _ in range(len(routing_requests))]
        routes_indexes_to_plan = [i for i in range(len(routing_requests))]
        counter = 1
        while routes_indexes_to_plan:
            remaining_routes = [routing_requests[route_index] for route_index in routes_indexes_to_plan]
            cbs = CBS()
            new_plan = cbs.solve(warehouse, remaining_routes, self.window)
            indexes_to_remove = []
            for i, route_index in enumerate(routes_indexes_to_plan):
                for j in range(min(self.time_to_plan, len(new_plan[i]))):
                    plan[route_index].append(new_plan[i][j])
                if plan[route_index][-1] == routing_requests[route_index].destination.coordinates:
                    indexes_to_remove.append(route_index)
                else:
                    new_source_coordinates = new_plan[i][self.time_to_plan]
                    routing_requests[route_index].source = warehouse.vertices[new_source_coordinates[0]][new_source_coordinates[1]]
                    if routing_requests[route_index].source == routing_requests[route_index].destination:
                        plan[route_index].append(new_source_coordinates)
                        indexes_to_remove.append(route_index)
            for index in indexes_to_remove:
                routes_indexes_to_plan.remove(index)
            for route in plan:
                print(route)
            is_deadlock = deadlock_detector(plan, warehouse, routing_requests, counter)
            if is_deadlock:
                self.time_to_plan = self.time_to_plan*2
                self.window = self.time_to_plan + 1
            counter += 1
        return plan


def deadlock_detector(plan, warehouse, routing_requests, counter):
    """
    Deals only with deadlocks caused by robots that wait in sources.
    If wait outside the warehouse' sources is allowed, need to implement deadlock detector to deal with that.
    """
    number_of_agents_not_at_sources = 0
    for route in plan:
        coordinates = route[-1]
        vertex_node = warehouse.vertices[coordinates[0]][coordinates[1]]
        if vertex_node not in warehouse.sources:
            number_of_agents_not_at_sources += 1
    sources_num = len(warehouse.sources)
    if number_of_agents_not_at_sources == len(routing_requests):
        return False
    if number_of_agents_not_at_sources < sources_num*counter:
        return True
    return False

from CBS.CBS import CBS

# TODO: dealing with waiting between windows


class RHCR:
    """
    window - the plan is free of conflicts until window
    time_to_plan - time to run CBS again
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
        while routes_indexes_to_plan:
            remaining_routes = [routing_requests[route_index] for route_index in routes_indexes_to_plan]
            cbs = CBS()
            new_plan = cbs.solve(warehouse, remaining_routes, self.window)
            # print("The new plan solved by CBS:")
            # for route in new_plan:
            #     print(route)
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
        return plan



from typing import Tuple, List

import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
from colorsys import hls_to_rgb
from copy import deepcopy
from time import time

from EnvironmentUtils import get_source_id_from_route, get_destination_id_from_route
from RouteGenerationAlgorithms import ROUTE_GENERATION_ALGORITHMS_ABBR

SHOW_ANIMATION_TRAIL = False

COLOR_BY_DESTINATION_ID = False
COLOR_BY_SOURCE_ID = False

WAREHOUSE_FPS = [24, 3, 6, 12]
distinct_colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), 'xkcd:dark pastel green', 'xkcd:strong pink', '#6dedfd',
                   (1, 0.5, 0.25), 'xkcd:light navy blue', (0.5, 0.25, 1)]  # len(distinct_colors) = 9


def plan_to_frames(plan):
    frames = []
    plan_copy = deepcopy(plan)
    appended = True

    while appended:
        appended = False
        frame = []
        for i in range(len(plan_copy)):
            if plan_copy[i]:
                frame.append(plan_copy[i].pop(0))
                appended = True
            else:
                frame.append([])

        if appended:
            frames.append(frame)

    return frames


def routing_request_plan_to_frames(routing_request_plan):
    return [[step] for step in routing_request_plan]


def random_color():
    return hls_to_rgb(random.random(), 0.25 + random.random() / 2.0, 0.25 + random.random() * (3.0 / 4.0))


def color_by_target_id(warehouse, plan, is_target_destination=True):
    routing_request_routes = []

    id_getter_function = get_destination_id_from_route if is_target_destination else get_source_id_from_route
    for route in plan:
        routing_request_target_id = id_getter_function(warehouse, route)

        routing_request_routes.append(
            plt.plot([], [], 'ro', c=distinct_colors[routing_request_target_id % len(distinct_colors)])[0])

    return routing_request_routes


def color_by_destination_id(warehouse, plan):
    return color_by_target_id(warehouse, plan)


def color_by_source_id(warehouse, plan):
    return color_by_target_id(warehouse, plan, False)


def remove_duplicate_destinations_from_route(route):
    if route[-1] != route[-2]:
        return route
    for i, (item1, item2) in enumerate(zip(route[::-1], route[:-1][::-1])):
        if item1 != item2:
            return route[:-i]


def set_routing_solution_title_and_info(warehouse, plan, running_time, algorithm_name, title):
    sum_of_costs = sum([len(remove_duplicate_destinations_from_route(route)) for route in plan])
    obstacle_density = round(len(warehouse.static_obstacles) / (warehouse.width * warehouse.length), 2)

    title_left = "map_size = " + str(warehouse.width) + "*" + str(warehouse.length) + \
                 "        obstacle_density = " + str(obstacle_density) + \
                 "\n(num_sources, num_destinations) = " + \
                 str((warehouse.number_of_sources, warehouse.number_of_destinations)) + \
                 "        num_agents = " + str(len(plan)) + \
                 "\nAlgorithm = " + algorithm_name + "        sum_of_costs = " + str(sum_of_costs) + \
                 "        running_time = " + str(running_time)

    plt.title(title_left, loc='left')
    plt.suptitle(title)


def set_path_generation_title_and_info(warehouse, plan, running_time, algorithm_name, title):
    source_id = get_source_id_from_route(warehouse, plan[0])
    destination_id = get_destination_id_from_route(warehouse, plan[0])

    title_left = "map_size = " + str(warehouse.width) + "*" + str(warehouse.length) + \
                 "        (source_id, destination_id) = " + str((source_id, destination_id)) + \
                 "\nalgorithm = " + algorithm_name + "        running_time = " + str(running_time) + \
                 "        num_routes_generated = " + str(len(plan))

    plt.title(title_left, loc='left')
    plt.suptitle(title)


def set_plot_title_and_info(warehouse, plan, running_time, algorithm_name, title):
    if algorithm_name in ROUTE_GENERATION_ALGORITHMS_ABBR:
        set_path_generation_title_and_info(warehouse, plan, running_time, algorithm_name, title)
    else:
        set_routing_solution_title_and_info(warehouse, plan, running_time, algorithm_name, title)


def show_plan_as_animation(warehouse, plan, algorithm_name="TODO", running_time=-1.0, title="", export_animation=False):
    fig, ax = warehouse.plot_layout()
    set_plot_title_and_info(warehouse, plan, running_time, algorithm_name, title)

    if COLOR_BY_DESTINATION_ID:
        routing_request_routes = color_by_destination_id(warehouse, plan)
    elif COLOR_BY_SOURCE_ID:
        routing_request_routes = color_by_source_id(warehouse, plan)
    else:
        routing_request_routes = [plt.plot([], [], 'ro', c=random_color())[0] for _ in range(len(plan))]

    frames = plan_to_frames(plan)
    xdata = [[] for _ in range(len(plan))]
    ydata = [[] for _ in range(len(plan))]

    def init():
        for routing_request_route in routing_request_routes:
            routing_request_route.set_data([], [])
        return routing_request_routes

    def animate(frame):
        for i, routing_request_route in enumerate(routing_request_routes):
            if frame[i]:
                if SHOW_ANIMATION_TRAIL:
                    if frame == frames[0]:
                        xdata[i] = [frame[i][1]]
                        ydata[i] = [frame[i][0]]
                    else:
                        xdata[i].append(frame[i][1])
                        ydata[i].append(frame[i][0])
                else:
                    routing_request_route.set_data([frame[i][1], frame[i][0]])

        if SHOW_ANIMATION_TRAIL:
            for i, routing_request_route in enumerate(routing_request_routes):
                routing_request_route.set_data(xdata[i], ydata[i])
        return routing_request_routes

    t0 = time()
    animate(frames[0])
    t1 = time()
    fps = WAREHOUSE_FPS[warehouse.warehouse_id - 1]
    dt = 1. / fps

    interval = 1000 * dt - (t1 - t0)

    animation = FuncAnimation(fig, animate, frames=frames, init_func=init, blit=True, interval=interval)

    plt.show()
    if export_animation:
        print("***")
        print("Exporting animation")
        animation.save('animation.gif', writer='ffmpeg')
        print("Export done")


def show_plan_as_image(warehouse, plan, running_time=-1.0, algorithm_name="TODO", title="", export_image=False):
    warehouse.plot_layout()
    if algorithm_name in ROUTE_GENERATION_ALGORITHMS_ABBR:
        set_path_generation_title_and_info(warehouse, plan, running_time, algorithm_name, title)
    else:
        set_plot_title_and_info(warehouse, plan, running_time, algorithm_name, title)

    for i, route in enumerate(plan):
        for coordinates in route:
            if COLOR_BY_DESTINATION_ID:
                plt.scatter(coordinates[1], coordinates[0], s=20,
                            color=distinct_colors[
                                get_destination_id_from_route(warehouse, route) % len(distinct_colors)])
            else:  # colors by source_id
                plt.scatter(coordinates[1], coordinates[0], s=20, color=distinct_colors[i % len(distinct_colors)])
    if export_image:
        print("***")
        print("Exporting figure")
        plt.savefig('figure.png')
        print("Export done")
    plt.show()


def visualize_plan(warehouse, plan, algorithm_name, running_time=-1, visualization_type="animation", title="",
                   is_export_visualization=False):
    if visualization_type == "animation":
        show_plan_as_animation(warehouse, plan, algorithm_name, running_time, title, is_export_visualization)
    if visualization_type == "image":
        show_plan_as_image(warehouse, plan, algorithm_name, running_time, title, is_export_visualization)

    else:
        print("visualization_type must be in", ["animation", "image"])

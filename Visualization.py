import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
from colorsys import hls_to_rgb
from copy import deepcopy
from time import time


SHOW_ANIMATION = True
EXPORT_ANIMATION = False
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


def agent_plan_to_frames(agent_plan):
    return [[step] for step in agent_plan]


def random_color():
    return hls_to_rgb(random.random(), 0.25 + random.random() / 2.0, 0.25 + random.random() * (3.0 / 4.0))


def get_destination_id(warehouse, route):
    agent_final_coordinates = route[-1]
    agent_destination = warehouse.vertices[agent_final_coordinates[0]][agent_final_coordinates[1]]
    return agent_destination.destination_id


def get_source_id(warehouse, route):
    agent_initial_coordinates = route[0]
    agent_source = warehouse.vertices[agent_initial_coordinates[0]][agent_initial_coordinates[1]]
    return agent_source.source_id


def color_by_target_id(warehouse, plan, is_target_destination=True):
    agent_routes = []

    id_getter_function = get_destination_id if is_target_destination else get_source_id
    for route in plan:
        agent_target_id = id_getter_function(warehouse, route)

        agent_routes.append(plt.plot([], [], 'ro', c=distinct_colors[agent_target_id % len(distinct_colors)])[0])

    return agent_routes


def color_by_destination_id(warehouse, plan):
    return color_by_target_id(warehouse, plan)


def color_by_source_id(warehouse, plan):
    return color_by_target_id(warehouse, plan, False)


def show_plan_as_animation(warehouse, plan, running_time=-1.0, algorithm_name="TODO", title=""):
    fig, ax = warehouse.plot_layout()
    set_plot_title_and_info(warehouse, plan, running_time, algorithm_name, title)

    if COLOR_BY_DESTINATION_ID:
        agent_routes = color_by_destination_id(warehouse, plan)
    elif COLOR_BY_SOURCE_ID:
        agent_routes = color_by_source_id(warehouse, plan)
    else:
        agent_routes = [plt.plot([], [], 'ro', c=random_color())[0] for _ in range(len(plan))]

    frames = plan_to_frames(plan)
    xdata = [[] for _ in range(len(plan))]
    ydata = [[] for _ in range(len(plan))]

    def init():
        for agent_route in agent_routes:
            agent_route.set_data([], [])
        return agent_routes

    def animate(frame):
        for i, agent_route in enumerate(agent_routes):
            if frame[i]:
                if SHOW_ANIMATION_TRAIL:
                    if frame == frames[0]:
                        xdata[i] = [frame[i][1]]
                        ydata[i] = [frame[i][0]]
                    else:
                        xdata[i].append(frame[i][1])
                        ydata[i].append(frame[i][0])
                else:
                    agent_route.set_data([frame[i][1], frame[i][0]])

        if SHOW_ANIMATION_TRAIL:
            for i, agent_route in enumerate(agent_routes):
                agent_route.set_data(xdata[i], ydata[i])
        return agent_routes

    t0 = time()
    animate(frames[0])
    t1 = time()
    fps = WAREHOUSE_FPS[warehouse.warehouse_id - 1]
    dt = 1. / fps

    interval = 1000 * dt - (t1 - t0)
    animation = FuncAnimation(fig, animate, frames=frames, init_func=init, blit=True, interval=interval)

    plt.show()
    if EXPORT_ANIMATION:
        animation.save('animation.gif', writer='ffmpeg')


def show_plan_as_image(warehouse, plan, running_time=-1.0, algorithm_name="TODO", title=""):
    warehouse.plot_layout()
    set_plot_title_and_info(warehouse, plan, running_time, algorithm_name, title)

    for i, route in enumerate(plan):
        for coordinates in route:
            if COLOR_BY_DESTINATION_ID:
                plt.scatter(coordinates[1], coordinates[0], color=distinct_colors[get_destination_id(warehouse, route) % warehouse.number_of_sources])
            else:   # colors by source_id
                plt.scatter(coordinates[1], coordinates[0], color=distinct_colors[i % warehouse.number_of_sources])
    plt.show()


def set_plot_title_and_info(warehouse, plan, running_time, algorithm_name, title):
    sum_of_costs = sum([len(route) for route in plan])

    title_left = "map_size = " + str(warehouse.width) + "*" + str(warehouse.length) + \
                 "        (num_sources, num_destinations) = " + \
                 str((warehouse.number_of_sources, warehouse.number_of_destinations)) + \
                 "        num_agents = " + str(len(plan)) + \
                 "\nAlgorithm = " + algorithm_name + "        sum_of_costs = " + str(sum_of_costs) + \
                 "        running_time = " + str(running_time)

    plt.title(title_left, loc='left')
    plt.suptitle(title)


def show_plan(warehouse, plan, running_time=-1.0, algorithm_name="TODO", title=""):
    if SHOW_ANIMATION:
        show_plan_as_animation(warehouse, plan, running_time, algorithm_name, title)
    else:
        show_plan_as_image(warehouse, plan, running_time, algorithm_name, title)

import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
from colorsys import hls_to_rgb
from copy import deepcopy
from time import time


EXPORT_ANIMATION = True
SHOW_ANIMATION_TRAIL = False
WAREHOUSE_FPS = [24, 3, 6, 12]


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


def show_plan_as_animation():
    #TODO
    pass


def show_plan_as_image():
    #TODO
    pass


def show_plan(warehouse, plan, running_time=-1.0, algorithm_name="TODO", dest_ids=None, title="", is_animation=True):
    fig, ax = warehouse.plot_layout()

    # colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), 'xkcd:dark pastel green', 'xkcd:strong pink', '#6dedfd', (1, 0.5, 0.25),
    #           'xkcd:light navy blue', (0.5, 0.25, 1)]
    # if warehouse.warehouse_id == 1:
    #     agent_routes = []
    #     for dest_id in dest_ids:
    #         # if dest_id > 2:
    #         #     continue
    #         agent_routes.append(plt.plot([], [], 'ro', c=colors[dest_id])[0])
    # else:
    #     agent_routes = []
    #     for i in range(len(plan)):
    #         if i == 20:
    #             agent_routes.append(plt.plot([], [], 'ro', c=colors[1])[0])
    #         else:
    #             agent_routes.append(plt.plot([], [], 'ro', c=colors[0])[0])

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

    sum_of_costs = sum([len(route) for route in plan])

    title_left = "map_size = " + str(warehouse.width) + "*" + str(warehouse.length) +\
                 "        (num_sources, num_destinations) = " + \
                 str((warehouse.number_of_sources, warehouse.number_of_destinations)) + \
                 "        num_agents = " + str(len(plan)) + \
                 "\nAlgorithm = " + algorithm_name + "        sum_of_costs = " + str(sum_of_costs) + \
                 "        running_time = " + str(running_time)

    plt.title(title_left, loc='left')
    plt.suptitle(title)
    plt.show()
    if EXPORT_ANIMATION:
        animation.save('animation.gif', writer='ffmpeg')

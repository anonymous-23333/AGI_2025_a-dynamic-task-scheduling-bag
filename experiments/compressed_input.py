import copy
import random

import numpy as np
from tqdm import tqdm

import config
from bag import Bag, BagWithDormantLevel
from improved_bag import ImprovedBag
from statistic_property_test import static_property_test
from utils import observing_evaluation, plot_static_properties, plot_dynamic_properties

show_intermediate_results = False

experiments_list = [["low speed input", "high capacity", "near future"],
                    ["low speed input", "high capacity", "distant future"],
                    ["low speed input", "low capacity", "near future"],
                    ["low speed input", "low capacity", "distant future"],
                    ["high speed input", "high capacity", "near future"],
                    ["high speed input", "high capacity", "distant future"],
                    ["high speed input", "low capacity", "near future"],
                    ["high speed input", "low capacity", "distant future"]
                    ]

image_1_1 = []
image_1_2 = []
image_2_1 = []
image_2_2 = []

# compressed input
original_data = []
for i in range(config.num_levels):
    priority = (np.linspace(0, 1, config.num_levels + 1)[i] + np.linspace(0, 1, config.num_levels + 1)[i + 1]) / 2
    original_data.append(priority * 0.5)
original_data += [original_data[-1]] * 10
random.shuffle(original_data)
original_data *= 10000

for input_speed, capacity, static_property_scope in experiments_list:

    data = copy.deepcopy(original_data)

    if input_speed == "low speed input":
        input_speed = config.input_speed_L
    elif input_speed == "high speed input":
        input_speed = config.input_speed_U
    else:
        input_speed = config.input_speed_L

    if capacity == "low capacity":
        capacity = config.level_capacity_L
    elif capacity == "high capacity":
        capacity = config.level_capacity_U
    else:
        capacity = config.level_capacity_L

    if static_property_scope == "near future":
        static_property_scope = config.static_property_range_L
    elif static_property_scope == "distant future":
        static_property_scope = config.static_property_range_H
    else:
        static_property_scope = config.static_property_range_L

    IB = ImprovedBag(config.num_levels, capacity)
    B = Bag(config.num_levels, capacity)
    Bwd = BagWithDormantLevel(config.num_levels, capacity)

    # load placeholders to the IB
    counter = 0
    r = {}

    for i in range(config.num_levels):
        priority = (np.linspace(0, 1, config.num_levels + 1)[i] + np.linspace(0, 1, config.num_levels + 1)[i + 1]) / 2
        for _ in range(config.num_placeholders):
            idx = -(counter + 1)
            IB.data[i].append([priority, idx])
            r[idx] = [priority, 0]
            counter += 1

    counter = 0

    numerical_evaluation_IB = []
    numerical_evaluation_B = []
    numerical_evaluation_Bwd = []

    for c in tqdm(range(config.num_full_swings)):

        numerical_evaluation_IB_tmp = []
        numerical_evaluation_B_tmp = []
        numerical_evaluation_Bwd_tmp = []

        for _ in range(len(IB.distributor_out) * 1):

            # take a task and return

            t = IB.take_out()
            if t is not None:
                if t[1] < 0:
                    IB.data[int(t[0] * config.num_levels)].append(t)
                else:
                    t[0] *= config.decay
                    IB.put_in(*t)
            tmp = static_property_test(IB, copy.deepcopy(r), static_property_scope, 10, False, "r")
            numerical_evaluation_IB_tmp.append(observing_evaluation(tmp))

            t = B.take_out()
            if t is not None:
                t[0] *= config.decay
                B.put_in(*t)
            tmp = static_property_test(B, copy.deepcopy(r), static_property_scope, 10, False, "g")
            numerical_evaluation_B_tmp.append(observing_evaluation(tmp))

            t = Bwd.take_out()
            if t is not None:
                t[0] *= config.decay
                Bwd.put_in(*t)
            tmp = static_property_test(Bwd, copy.deepcopy(r), static_property_scope, 10, False, "b")
            numerical_evaluation_Bwd_tmp.append(observing_evaluation(tmp))

            # put mew tasks

            for _ in range(input_speed):
                while data:
                    priority = data.pop()
                    IB.put_in(priority, counter)
                    B.put_in(priority, counter)
                    Bwd.put_in(priority, counter)
                    r[counter] = [priority, 0]
                    counter += 1
                    break

        numerical_evaluation_IB += numerical_evaluation_IB_tmp
        numerical_evaluation_B += numerical_evaluation_B_tmp
        numerical_evaluation_Bwd += numerical_evaluation_Bwd_tmp

    ret_IB = static_property_test(IB, copy.deepcopy(r), static_property_scope, 10, show_intermediate_results, "#f4a582")
    ret_B = static_property_test(B, copy.deepcopy(r), static_property_scope, 10, show_intermediate_results, "#b2d8b2")
    ret_Bwd = static_property_test(Bwd, copy.deepcopy(r), static_property_scope, 10, show_intermediate_results,
                                   "#92c5de")

    if input_speed == config.input_speed_L:
        image_1_1.append([ret_IB, ret_B, ret_Bwd])
        image_1_2.append([numerical_evaluation_IB, numerical_evaluation_B, numerical_evaluation_Bwd,
                          capacity, static_property_scope])
    else:
        image_2_1.append([ret_IB, ret_B, ret_Bwd])
        image_2_2.append([numerical_evaluation_IB, numerical_evaluation_B, numerical_evaluation_Bwd,
                          capacity, static_property_scope])

plot_static_properties(image_1_1)
plot_static_properties(image_2_1)
plot_dynamic_properties(image_1_2)
plot_dynamic_properties(image_2_2)

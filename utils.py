import math

import numpy as np
from matplotlib import pyplot as plt

import config


def gen_distributor(num_levels):
    capacity = (num_levels * (num_levels + 1)) // 2
    distributor = [-1] * capacity
    index = 0

    for rank in range(num_levels, 0, -1):
        for _ in range(rank):
            index = ((capacity // rank) + index) % capacity
            while distributor[index] >= 0:
                index = (index + 1) % capacity
            distributor[index] = rank - 1
    return distributor


def functioning_evaluation(seq, eps_var: float = 1e-12, eps_mean: float = 1e-12) -> float:
    # considering linearity and increasing
    n = len(seq)
    if n < 3:
        return 0.0
    diffs = [seq[i + 1] - seq[i] for i in range(n - 1)]
    mean_d = sum(diffs) / (n - 1)
    var = sum((d - mean_d) ** 2 for d in diffs) / (n - 1)
    if var < eps_var and mean_d > eps_mean:
        return 0.0
    penalty = 0.0 if mean_d > eps_mean else 1.0
    return math.sqrt(var) / (abs(mean_d) + eps_var) + penalty


def observing_evaluation(seq):
    # only # considering linearity
    sequence = np.array(seq)
    x = np.arange(len(sequence))
    y = sequence

    a, b = np.polyfit(x, y, deg=1)
    y_fit = a * x + b

    mae = np.mean(np.abs(y - y_fit))
    return mae


def plot_static_properties(groups):
    labels = list(range(10))
    colors = ["#f4a582", "#b2d8b2", "#92c5de"]
    n_positions = len(groups[0][0])
    n_groups = len(groups)
    n_layers = len(groups[0])

    x = np.arange(n_positions)
    width = 0.2
    offsets = np.linspace(-1.5 * width, 1.5 * width, n_groups)

    fig, ax = plt.subplots()

    for g in range(n_groups):
        group = groups[g]
        for i in range(n_positions):
            values = [group[layer][i] for layer in range(n_layers)]
            sorted_indices = np.argsort(values)
            sorted_values = [values[j] for j in sorted_indices]
            sorted_colors = [colors[j] for j in sorted_indices]

            prev_value = 0
            for val, color in zip(sorted_values, sorted_colors):
                height = val - prev_value
                if height > 0:
                    ax.bar(x[i] + offsets[g], height, width, bottom=prev_value, color=color)
                prev_value = val

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Index of Levels")
    ax.set_ylabel("Average Number of Processing")

    legend_labels = ["IB", "B", "Bwd"]
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i]) for i in range(n_layers)]
    ax.legend(handles, legend_labels)

    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_dynamic_properties(groups):
    colors = ["#f4a582", "#b2d8b2", "#92c5de"]  # IB, B, Bwd
    line_styles = ["-", "--", "-.", ":"]  # HL, HH, LL, LH
    plt.figure()
    plt.yscale("log")
    for numerical_evaluation_IB, numerical_evaluation_B, numerical_evaluation_Bwd, capacity, static_property_scope in groups:
        if capacity == config.level_capacity_L:
            if static_property_scope == config.static_property_range_L:
                line_style = line_styles[2]
                label = "LL"
            else:
                line_style = line_styles[3]
                label = "LH"
        else:
            if static_property_scope == config.static_property_range_L:
                line_style = line_styles[0]
                label = "HL"
            else:
                line_style = line_styles[1]
                label = "HH"
        print(label)
        plt.plot(list(range(10, len(numerical_evaluation_IB))), numerical_evaluation_IB[10:],
                 color=colors[0],
                 linestyle=line_style,
                 label=f"IB_{label}")
        plt.plot(list(range(10, len(numerical_evaluation_B))), numerical_evaluation_B[10:],
                 color=colors[1],
                 linestyle=line_style,
                 label=f"B_{label}")
        plt.plot(list(range(10, len(numerical_evaluation_Bwd))), numerical_evaluation_Bwd[10:],
                 color=colors[2],
                 linestyle=line_style,
                 label=f"Bwd_{label}")

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles, labels, ncol=4, bbox_to_anchor=(0.5, -0.15), loc="upper center")
    plt.xlabel("n-th Take-Out/Put-In")
    plt.ylabel("Evaluation")
    plt.grid()
    plt.tight_layout()
    plt.show()

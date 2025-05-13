import copy
from typing import Union

import matplotlib.pyplot as plt

from bag import Bag
from utils import functioning_evaluation


class ImprovedBag:
    pass


def static_property_test(bag: Union[Bag, ImprovedBag], record: dict, num_full_swings: int, num_repeat: int,
                         show: bool = False, color: str = "b"):
    bag = copy.deepcopy(bag)

    ret = [0 for _ in range(bag.num_levels)]

    for _ in range(num_repeat):
        for _ in range(num_full_swings):
            for _ in range(len(bag.distributor_out)):
                t = bag.take_out()
                if t is None:
                    continue
                c = 1
                while t[1] < 0:  # placeholder
                    level_idx = bag.distributor_out[bag.cursor_out]
                    bag.data[level_idx].append(t)
                    t = bag.take_out()
                    c += 1
                    if c > len(bag.distributor_out):
                        break
                level_idx = bag.distributor_out[bag.cursor_out]
                bag.data[level_idx].append(t)

                if t[1] >= 0:
                    record[t[1]][1] += 1

        bins = [[] for _ in range(bag.num_levels)]
        for each in record:
            priority, count = record[each]
            lv = min(int(priority * bag.num_levels), bag.num_levels - 1)
            bins[lv].append(count)
        avg_bin = [sum(each) / (len(each) + 0.01) for each in bins]
        ret = [ret[i] + avg_bin[i] for i in range(bag.num_levels)]

    ret = [each / num_repeat for each in ret]

    if show:
        # print(ret)
        plt.figure()
        plt.grid()
        plt.bar(range(bag.num_levels), ret, color=color)
        plt.xticks(range(bag.num_levels))
        plt.xlabel("Level Index")
        plt.ylabel("Average Processing for Each Level")
        plt.show()
        # print(record)

    return ret


if __name__ == "__main__":

    B = Bag(3)

    # d = {0: [0.1], 1: [0.5], 2: [0.9] * 1}
    # d = {0: [0.1], 1: [0.5], 2: [0.9] * 2}
    # d = {0: [0.1], 1: [0.5, 0.9], 2: [0.9] * 1}
    # d = {0: [0.1, 0.9], 1: [0.5], 2: [0.9] * 1}

    # d = {0: [0.1], 1: [0.5], 2: [0.9] * 10}
    d = {0: [0.1] + [0.9] * 3, 1: [0.5] + [0.9] * 3, 2: [0.9] * 4}

    r = {}
    counter = 0
    for lvl in d:
        for prio in d[lvl]:
            B.data[lvl].append([prio, counter])
            r[counter] = [prio, 0]
            counter += 1

    M = [B.distributor_out.count(i) for i in range(B.num_levels)]
    N, P = [0 for _ in range(B.num_levels)], []
    for each_level in B.data:
        tmp = [0 for _ in range(B.num_levels)]
        for each_task in each_level:
            lv: int = int(each_task[0] // (1 / B.num_levels))
            tmp[lv] += 1
            N[lv] += 1
        tmp = [each / sum(tmp) for each in tmp]
        P.append(tmp)
    S = []
    for i in range(len(M)):
        tmp = 0
        for j in range(len(M)):
            tmp += M[j] * P[j][i]
        S.append(tmp)
    evaluation = functioning_evaluation(S)
    print([S[i] / (N[i] + 1e-5) for i in range(B.num_levels)])

    static_property_test(B, r, 100, 10)

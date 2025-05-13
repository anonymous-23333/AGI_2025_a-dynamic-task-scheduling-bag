import copy

from utils import functioning_evaluation, gen_distributor

max_diff = 5


class ImprovedBag:

    def __init__(self, num_levels: int, level_capacity):

        self.num_levels: int = num_levels
        self.level_capacity = level_capacity
        self.data: list[list[list[float, any], ...], ...] = [[] for _ in range(num_levels)]

        self.cursor_out: int = 0
        self.distributor_out: list[int, ...] = gen_distributor(num_levels)

    def put_in(self, value: float, item: any) -> None:

        lv_ought_to_be = int(value * self.num_levels)
        if len(self.data[lv_ought_to_be]) - min([len(_each) for _each in self.data]) <= max_diff:
            self.data[lv_ought_to_be].append([value, item])
            return

        tmp = []
        num_tasks = [len(each_level) for each_level in self.data]
        for lv in range(self.num_levels):
            # if num_tasks[lv] + 1 - min(num_tasks) > max_diff:
            #     continue
            tmp.append(self.dip(value, item, lv, self.data))
        lv = tmp.index(min(tmp))
        self.data[lv].append([value, item])
        if len(self.data[lv]) > self.level_capacity:
            to_pop = self.data[lv].pop(0)
            if to_pop[1] < 0:
                self.data[lv].append(to_pop)

    def dip(self, value: float, item: any, lv: int, data: list[list[list[float, any], ...], ...]):
        dc = copy.deepcopy(data)
        dc[lv].append([value, item])
        # L, the number of processing of each level
        L = [self.distributor_out.count(i) for i in range(self.num_levels)]
        M, P = self.calc_mp(dc)
        T = self.calc_t(L, P)
        evaluation = functioning_evaluation([T[i] / (M[i] + 1e-5) for i in range(self.num_levels)])
        return evaluation

    def calc_mp(self, data) -> tuple[list[int, ...], list[list[float, ...], ...]]:
        # M, the number of tasks of each type of priority
        # P, the proportion of tasks of each type of priority in each level
        M, P = [0 for _ in range(self.num_levels)], []
        for i, each_level in enumerate(data):
            tmp = [0 for _ in range(self.num_levels)]
            for each_task in each_level:
                lv: int = int(each_task[0] // (1 / self.num_levels))
                M[lv] += 1
                tmp[lv] += 1
            tmp = [each / (sum(tmp) + 1e-5) for each in tmp]
            P.append(tmp)
        return M, P

    def calc_t(self, L: list[int, ...], P: list[list[float, ...], ...]) -> list[float, ...]:
        T = []
        for i in range(self.num_levels):
            tmp = 0
            for j in range(len(L)):
                tmp += L[j] * P[j][i]
            T.append(tmp)
        return T

    def take_out(self) -> any:
        count: int = 1
        self.cursor_out = (self.cursor_out + 1) % len(self.distributor_out)
        # while self.cursor_out >= 5:
        #     self.cursor_out = (self.cursor_out + 1) % len(self.distributor_out)
        while not self.data[self.distributor_out[self.cursor_out]]:
            count += 1
            if count > len(self.distributor_out):
                return None
            self.cursor_out = (self.cursor_out + 1) % len(self.distributor_out)
            # while self.cursor_out >= 5:
            #     self.cursor_out = (self.cursor_out + 1) % len(self.distributor_out)
        ret = self.data[self.distributor_out[self.cursor_out]].pop(0)
        return ret

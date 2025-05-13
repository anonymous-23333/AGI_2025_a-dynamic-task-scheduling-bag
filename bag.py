from utils import gen_distributor


class Bag:

    def __init__(self, num_levels: int, level_capacity):

        self.num_levels: int = num_levels
        self.level_capacity = level_capacity
        self.data: list[list[list[float, any], ...], ...] = [[] for _ in range(num_levels)]

        self.cursor_out: int = 0
        self.distributor_out: list[int, ...] = gen_distributor(num_levels)

    def clear(self):
        self.data = [[] for _ in range(self.num_levels)]
        self.cursor_out: int = 0

    def put_in(self, value: float, item: any) -> None:
        lv: int = int(value // (1 / self.num_levels))
        self.data[lv].append([value, item])
        # if sum([len(each_level) for each_level in self.data]) > self.num_levels * limit:
        #     self.data[0].pop(0)
        if len(self.data[lv]) > self.level_capacity:
            self.data[lv].pop(0)

    def take_out(self) -> any:
        count: int = 1
        self.cursor_out = (self.cursor_out + 1) % len(self.distributor_out)
        while not self.data[self.distributor_out[self.cursor_out]]:
            count += 1
            if count > len(self.distributor_out):
                return None
            self.cursor_out = (self.cursor_out + 1) % len(self.distributor_out)
        ret = self.data[self.distributor_out[self.cursor_out]].pop(0)
        return ret


class BagWithDormantLevel(Bag):

    def __init__(self, num_levels: int, level_capacity, dormant_threshold: float = 0.1):
        super().__init__(num_levels, level_capacity)
        # for levels correspond to priority < this threshold, they are dormant
        self.dormant_threshold = dormant_threshold
        self.remaining_processing_this_level = 0

    def take_out(self) -> any:
        count: int = 1
        if self.remaining_processing_this_level <= 0:
            self.cursor_out = (self.cursor_out + 1) % len(self.distributor_out)
        while not self.data[self.distributor_out[self.cursor_out]]:
            count += 1
            if count > len(self.distributor_out):
                return None
            self.cursor_out = (self.cursor_out + 1) % len(self.distributor_out)
        if self.remaining_processing_this_level <= 0:
            self.remaining_processing_this_level = len(self.data[self.distributor_out[self.cursor_out]])
        ret = self.data[self.distributor_out[self.cursor_out]].pop(0)
        self.remaining_processing_this_level -= 1
        return ret

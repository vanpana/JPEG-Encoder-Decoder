import math
from copy import deepcopy

from src.domain.exceptions.InvalidSizeException import InvalidSizeException


class Block:
    def __init__(self, items, pos):
        self.block_size = int(math.sqrt(len(items)))
        self.items = deepcopy(items)
        self.position_in_image = pos

    def shrink(self, shrink_times=4):
        step = self.block_size // shrink_times
        new_items = []
        for line in range(0, self.block_size, step):
            for col in range(0, self.block_size, step):
                full_item = [self.items[int(math.sqrt(self.block_size)) * i + j] for i in range(line, line + step) for j in
                             range(col, col + step)]
                new_items.append(sum(full_item) / shrink_times)
        self.items = new_items

    def grow(self, to_size):
        pass

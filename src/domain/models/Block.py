import math
from copy import deepcopy


class Block:
    def __init__(self, items, pos):
        self.block_size = int(math.sqrt(len(items)))
        self.items = deepcopy(items)
        self.position_in_image = pos

    def shrink(self, shrink_times=4):
        step = self.block_size // shrink_times
        new_items = []
        for line in range(0, self.block_size - 1, step):
            for col in range(0, self.block_size - 1, step):
                full_item = [self.items[self.block_size * i + j] for i in range(line, line + step) for j
                             in range(col, col + step)]
                new_items.append(sum(full_item) / len(full_item))
        self.items = new_items
        self.block_size = step

    def grow(self, grow_times=4):
        step = self.block_size * grow_times
        new_items = []

        for chunk in [self.items[i:i + grow_times] for i in range(0, len(self.items), grow_times)]:
            duplicated = [x for pair in zip(chunk, chunk) for x in pair]
            new_items.extend(duplicated)
            new_items.extend(duplicated)

        self.items = new_items
        self.block_size = step

    def __str__(self):
        return str(self.items)

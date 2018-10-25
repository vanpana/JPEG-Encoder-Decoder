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
        for line in range(0, self.block_size, step):
            for col in range(0, self.block_size, step):
                full_item = [self.items[int(math.sqrt(self.block_size)) * i + j] for i in range(line, line + step) for j
                             in
                             range(col, col + step)]
                new_items.append(sum(full_item) / shrink_times)
        self.items = new_items
        self.block_size = step

    def grow(self, grow_times=4):
        step = self.block_size * grow_times
        new_items = [0 for _ in range(0, step * step)]
        for i in range(0, len(self.items), grow_times // 2):
            for j in range(0, grow_times // 2):
                new_items[i + j] = self.items[i]
                new_items[i + j + 8] = self.items[i]
        self.items = new_items
        self.block_size = step


'''
1 1 2 2 3 3 4 4
1 1 2 2 3 3 4 4
5 5 6 6 7 7 8 8
5 5 6 6 7 7 8 8

1 1 2 2 3 3 4 4
1 1 2 2 3 3 4 4
5 5 6 6 7 7 8 8
5 5 6 6 7 7 8 8
'''

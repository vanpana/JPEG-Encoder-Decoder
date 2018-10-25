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
        new_items = []

        for chunk in [self.items[i:i + grow_times] for i in range(0, len(self.items), grow_times)]:
            duplicated = [x for pair in zip(chunk, chunk) for x in pair]
            new_items.extend(duplicated)
            new_items.extend(duplicated)

        self.items = new_items
        self.block_size = step


'''
1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16
1 1 2 2 3 3 4 4 1 1 2 2 3 3 4 4 5 5 6 6 7 7 8 8 5 5 6 6 7 7 8 8
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1

1 1 2 2 3 3 4 4
1 1 2 2 3 3 4 4
5 5 6 6 7 7 8 8
5 5 6 6 7 7 8 8
'''

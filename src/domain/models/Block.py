import math
from copy import deepcopy

from src.util import Global


class Block:
    def __init__(self, items, pos):
        self.block_size = len(items)
        self.items = deepcopy(items)  # Items = [[], [], ...]
        self.position_in_image = pos
        self.steps = None
        Global.position += 1

    def shrink(self, shrink_times=4):
        step = self.block_size // shrink_times
        new_items = []
        for col in range(0, self.block_size, step):
            for line in range(0, self.block_size, step):
                full_item = [self.items[i][j]
                             for j in range(col, col + step)
                             for i in range(line, line + step)]
                new_items.append(sum(full_item) / len(full_item))
        self.items = [new_items[i:i + 4] for i in range(0, len(new_items), shrink_times)]
        self.block_size = step * step

    def grow(self, grow_times=4):
        step = self.block_size * grow_times // 2
        new_items = [[0 for _ in range(0, step)] for _ in range(0, step)]

        for i in range(0, len(self.items)):
            for j in range(0, len(self.items[i])):
                item = self.items[i][j]
                ki = 2 * i
                kj = 2 * j
                new_items[ki][kj] = item
                new_items[ki][kj + 1] = item
                new_items[ki + 1][kj] = item
                new_items[ki + 1][kj + 1] = item

        self.items = new_items
        self.block_size = step

    def subtract_from_values(self, subtract_number=128):
        self.add_to_values(-subtract_number)

    def add_to_values(self, add_number=128):
        for i in range(0, len(self.items)):
            for j in range(0, len(self.items[i])):
                self.items[i][j] += add_number

    def get_entropy(self):
        self.__generate_steps()
        zig_zag_bytes = self.__get_zig_zag_bytes()
        pass

    def __get_zig_zag_bytes(self):
        return [self.items[tup[0]][tup[1]] for tup in self.steps]

    def __generate_steps(self):
        if self.steps is not None:
            return

        self.steps = []

        x = 0
        y = 0

        self.steps.append((y, x))

        while True:
            if x < self.block_size - 1:
                x += 1
            else:
                y += 1
            self.steps.append((y, x))

            while True:
                x -= 1
                y += 1

                self.steps.append((y, x))

                if x == 0 or y == self.block_size - 1:
                    break

            if y == 0 or y == self.block_size - 1:
                x += 1
            else:
                y += 1

            self.steps.append((y, x))

            if x == self.block_size - 1 and y == self.block_size - 1:
                break

            while True:
                y -= 1
                x += 1
                self.steps.append((y, x))
                if y == 0 or x == self.block_size - 1:
                    break

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.items)

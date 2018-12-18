import math
from copy import deepcopy

from src.util import Global


class Block:
    steps = None

    def __init__(self, items, pos):
        self.block_size = len(items)
        self.items = deepcopy(items)  # Items = [[], [], ...]
        self.position_in_image = pos
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
        return self.__encode(self.__get_zig_zag_bytes())

    @staticmethod
    def get_from_entropy(entropy):
        # Decode first
        zig_zag_bytes = [entropy[0][1]]

        for i in range(1, len(entropy)):
            if len(entropy[i]) == 3:
                # Append zeros
                while entropy[i][0] > 0:
                    zig_zag_bytes.append(0)
                    entropy[i] = (entropy[i][0] - 1, entropy[i][1], entropy[i][2])
                zig_zag_bytes.append(entropy[i][2])
            else:
                while len(zig_zag_bytes) < 64:
                    zig_zag_bytes.append(0)

        # Place back
        items = [[0 for _ in range(0, 8)] for _ in range(0, 8)]

        block = Block(items, Global.position)

        for i in range(0, len(Block.steps)):
            step = Block.steps[i]
            block.items[step[0]][step[1]] = zig_zag_bytes[i]

        return block

    def __get_zig_zag_bytes(self):
        return [self.items[tup[0]][tup[1]] for tup in Block.steps]

    def __generate_steps(self):
        if Block.steps is not None:
            return

        Block.steps = []

        x = 0
        y = 0

        Block.steps.append((y, x))

        while True:
            if x < self.block_size - 1:
                x += 1
            else:
                y += 1
            Block.steps.append((y, x))

            while True:
                x -= 1
                y += 1

                Block.steps.append((y, x))

                if x == 0 or y == self.block_size - 1:
                    break

            if y == 0 or y == self.block_size - 1:
                x += 1
            else:
                y += 1

            Block.steps.append((y, x))

            if x == self.block_size - 1 and y == self.block_size - 1:
                break

            while True:
                y -= 1
                x += 1
                Block.steps.append((y, x))
                if y == 0 or x == self.block_size - 1:
                    break

    def __encode(self, zig_zag_bytes):
        # Encode first
        encoded_bytes = [(self.__get_size(zig_zag_bytes[0]), zig_zag_bytes[0])]

        # Encode rest
        zero_count = 0

        for i in range(1, 64):
            if zig_zag_bytes[i] == 0:
                # Skip byte if 0
                zero_count += 1
                continue
            else:
                # Append the byte with the following tuple structure: (RUNLENGTH, SIZE, AMPLITUDE)
                encoded_bytes.append((zero_count, self.__get_size(zig_zag_bytes[i]), zig_zag_bytes[i]))

                # Reset zero count if needed
                if zero_count > 0:
                    zero_count = 0
        else:
            # If the sequence ends with zero bytes, append END-OF-BLOCK code
            if zero_count > 0:
                encoded_bytes.append((0, 0))

        return encoded_bytes

    def __get_size(self, amplitude):
        amplitude = int(round(amplitude))
        if amplitude == -1 or amplitude == 1:
            return 1
        elif amplitude == -3 or amplitude == -2 or amplitude == 2 or amplitude == 3:
            return 2
        elif amplitude in range(-7, -3) or amplitude in range(4, 8):
            return 3
        elif amplitude in range(-15, -7) or amplitude in range(8, 16):
            return 4
        elif amplitude in range(-31, -15) or amplitude in range(16, 32):
            return 5
        elif amplitude in range(-63, -31) or amplitude in range(32, 64):
            return 6
        elif amplitude in range(-127, -63) or amplitude in range(64, 128):
            return 7
        elif amplitude in range(-255, -127) or amplitude in range(128, 256):
            return 8
        elif amplitude in range(-511, -255) or amplitude in range(256, 512):
            return 9
        elif amplitude in range(-1023, -511) or amplitude in range(512, 1024):
            return 10

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.items)

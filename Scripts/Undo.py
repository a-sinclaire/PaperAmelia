#
# Author: Amelia Sinclaire
# Copyright 2023
#

from copy import deepcopy


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class UndoBuffer:
    def __init__(self, max_undos=10):
        self.max_undos = max_undos
        self.undo_buffer = []
        self.pointer = 0

    def add(self, state):
        # buffer empty, just append (only happens once)
        if len(self.undo_buffer) == 0:
            self.undo_buffer.append(deepcopy(state))

        self.pointer = clamp(self.pointer + 1, 0, self.max_undos)

        # history position is beyond the end of array
        if self.pointer > len(self.undo_buffer) - 1:
            # history list is at max len
            if len(self.undo_buffer) == self.max_undos:
                self.pointer -= 1
                self.undo_buffer.pop(0)  # remove oldest item if we exceed max undos
            self.undo_buffer.append(deepcopy(state))
            return

        # we must trim positions after current position, this way current position is most recent
        del self.undo_buffer[self.pointer + 1:]
        # save outfit to the current position
        self.undo_buffer[self.pointer] = deepcopy(state)
        return

    def undo(self):
        self.pointer = clamp(self.pointer - 1, 0, len(self.undo_buffer) - 1)
        return deepcopy(self.undo_buffer[self.pointer])

    def redo(self):
        self.pointer = clamp(self.pointer + 1, 0, len(self.undo_buffer) - 1)
        return deepcopy(self.undo_buffer[self.pointer])

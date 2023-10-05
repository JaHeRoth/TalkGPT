from enum import Enum


class Verbosity(Enum):
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


class Logger:
    def __init__(self, verbosity: Verbosity):
        self.verbosity = verbosity

    def log(self, message: str):
        if self.verbosity is Verbosity.VERBOSE:
            print(message)

    def priority_log(self, message: str):
        if self.verbosity is Verbosity.NORMAL or self.verbosity is Verbosity.VERBOSE:
            print('#' * 80)
            print(message)
            print('#' * 80)

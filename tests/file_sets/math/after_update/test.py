from typing import Union

from tests.file_sets.math.before_update.protocols import Arg1
def foo(arg: Union[Arg1, float, int]):
    arg /= 1
    arg //= 1
    arg *= 1
    arg -= 1
    arg **= 1
    arg %= 1
    arg = 1 / arg
    arg = 1 // arg
    arg = 1 * arg
    arg = 1 + arg
    arg = 1 - arg
    arg = 1 ** arg
    arg = 1 % arg
    return arg + 1

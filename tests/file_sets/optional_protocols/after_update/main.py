from typing import Union

from tests.file_sets.optional_protocols.before_update.protocols import Something1
def main(string: str, something: Something1, sequence_of_chars: Union[bytearray, bytes, str]):
    _ = string.startswith("")
    something.foo()
    sequence_of_chars.join([])

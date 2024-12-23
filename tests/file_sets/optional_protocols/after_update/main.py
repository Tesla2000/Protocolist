from tests.file_sets.optional_protocols.before_update.protocols import CharSequence
from tests.file_sets.optional_protocols.before_update.protocols import Something1
def main(string: str, something: Something1, sequence_of_chars: CharSequence):
    _ = string.startswith("")
    something.foo()
    sequence_of_chars.join([])

from io import BufferedIOBase
from io import BufferedRandom
from io import BufferedReader
from io import BufferedRWPair
from io import BufferedWriter
from io import BytesIO
from io import FileIO
from io import RawIOBase
from io import StringIO
from io import TextIOBase
from io import TextIOWrapper
from typing import Union
IOClass = Union[BufferedIOBase, BufferedRWPair, BufferedRandom, BufferedReader, BufferedWriter, BytesIO, FileIO, RawIOBase, StringIO, TextIOBase, TextIOWrapper]

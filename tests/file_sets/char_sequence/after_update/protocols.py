from typing import Protocol as ProtocolistProtocol
from typing import runtime_checkable
from typing import Self
from typing import Union
CharSequence = Union[str, bytes, bytearray]
@runtime_checkable
class Arg1(ProtocolistProtocol):
	def startswith(self, arg0: Union[CharSequence, Self]):
		...

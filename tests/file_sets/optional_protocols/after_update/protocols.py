from typing import Protocol as ProtocolistProtocol
from typing import runtime_checkable
from typing import Union
CharSequence = Union[str, bytes, bytearray]
@runtime_checkable
class Something1(ProtocolistProtocol):
	def foo(self):
		...

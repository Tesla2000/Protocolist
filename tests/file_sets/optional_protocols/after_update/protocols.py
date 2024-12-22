from typing import Protocol as ProtocolistProtocol
from typing import runtime_checkable
@runtime_checkable
class Something1(ProtocolistProtocol):
	def foo(self):
		...

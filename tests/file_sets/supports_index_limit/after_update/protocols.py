from typing import Protocol as ProtocolistProtocol
from typing import runtime_checkable
@runtime_checkable
class Array1(ProtocolistProtocol):
	def __getitem__(self, key):
		...

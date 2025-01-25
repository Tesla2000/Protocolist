from collections.abc import Collection
from typing import Protocol as ProtocolistProtocol
from typing import runtime_checkable
from typing import Union

@runtime_checkable
class Arg(ProtocolistProtocol):
	
	def __add__(self, other):
		...
@runtime_checkable
class Content(ProtocolistProtocol):
	content: Union["Content", Collection[Union["ContentSubscript", str]], memoryview]
	string: Union["ContentSubscript", str]
	def __iter__(self):
		...
	def __len__(self):
		...
@runtime_checkable
class ContentSubscript(ProtocolistProtocol):
	
	def startswith(self, arg0: str):
		...
@runtime_checkable
class Message(ProtocolistProtocol):
	content: "Content"
	role: "Role"
	def __getitem__(self, key):
		...
	def __iter__(self):
		...
	def some_method(self, arg0: str, arg1: Union[int, str], string: Union[list, str]):
		...
@runtime_checkable
class MessageSecondSubscript(ProtocolistProtocol):
	
	def count(self, arg0: str):
		...
@runtime_checkable
class Role(ProtocolistProtocol):
	
	def __delitem__(self, key):
		...
	def __getitem__(self, key):
		...
	def __iter__(self):
		...
	def __len__(self):
		...
	def __next__(self):
		...
	def __setitem__(self, key, value):
		...

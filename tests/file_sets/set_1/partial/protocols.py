from collections.abc import Collection
from typing import Protocol as ProtocolistProtocol
from typing import runtime_checkable
from typing import Union
@runtime_checkable
class Content2(ProtocolistProtocol):
	def __iter__(self):
		...
	def __len__(self):
		...
@runtime_checkable
class Message2FirstSubscript(ProtocolistProtocol):
	def startswith(self, arg0: str):
		...
@runtime_checkable
class Role1(ProtocolistProtocol):
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
@runtime_checkable
class Content1(ProtocolistProtocol):
	def __setitem__(self, key, value):
		...
	content: Union[Collection[Union[Message2FirstSubscript, str]], Content2, memoryview]
	string: Union[Message2FirstSubscript, str]
@runtime_checkable
class Message1(ProtocolistProtocol):
	content: Content1
	role: Role1
	def some_method(self, arg0: str, arg1: Union[int, str], string: Union[list, str]):
		...
@runtime_checkable
class Message2(ProtocolistProtocol):
	def __getitem__(self, key):
		...
	def __iter__(self):
		...
@runtime_checkable
class Message2SecondSubscript(ProtocolistProtocol):
	def count(self, arg0: str):
		...

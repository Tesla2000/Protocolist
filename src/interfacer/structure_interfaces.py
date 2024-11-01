from __future__ import annotations

from itertools import permutations
from typing import Protocol

import libcst

from src.interfacer.config import Config
from src.interfacer.transform.prototype_order import PrototypeOrder


def structure_interfaces(config: Config):
    interface_path = config.interfaces_path
    interfaces = {}
    code = interface_path.read_text()
    exec(code, interfaces)
    interfaces = {
        key: value
        for key, value in interfaces.items()
        if isinstance(value, type)
        and issubclass(value, Protocol)
        and value is not Protocol
    }
    inheritances = {}
    for interface1, interface2 in permutations(interfaces.keys(), 2):
        if issubclass(interfaces[interface1], interfaces[interface2]):
            inheritances[interface1] = interface2
        elif issubclass(interfaces[interface2], interfaces[interface1]):
            inheritances[interface2] = interface1
    module = libcst.parse_module(code)
    transformer = PrototypeOrder(module, config, inheritances)
    updated_module = module.visit(transformer)
    interface_path.write_text(updated_module.code)

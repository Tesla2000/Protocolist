from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Optional

from libcst import Annotation
from libcst import Import
from libcst import ImportFrom
from libcst import Index
from libcst import LeftSquareBracket
from libcst import MaybeSentinel
from libcst import Module
from libcst import Name
from libcst import Param
from libcst import RightSquareBracket
from libcst import SimpleString
from libcst import SimpleWhitespace
from libcst import Subscript
from libcst import SubscriptElement

from src.interfacer.config import Config
from src.interfacer.protocol_markers.mark_options import MarkOption
from src.interfacer.ProtocolDict import ProtocolDict


class TypeMarker(ABC):
    type: MarkOption

    def __init__(self, config: Config):
        self.config = config
        self.imported_interfaces = set()

    @abstractmethod
    def conv_parameter(
        self, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> "Param":
        pass

    @classmethod
    def _create_literal_annotation(
        cls, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> Optional[Annotation]:
        param_name = updated_node.name.value
        if param_name == "self":
            return
        protocols[param_name] += 1
        annotations[param_name + str(protocols[param_name])] = None
        return Annotation(
            annotation=Subscript(
                value=Name(
                    value="Literal",
                    lpar=[],
                    rpar=[],
                ),
                slice=[
                    SubscriptElement(
                        slice=Index(
                            value=SimpleString(
                                value=f"'{updated_node.name.value}"
                                f"{protocols[param_name]}'",
                                lpar=[],
                                rpar=[],
                            ),
                            star=None,
                            whitespace_after_star=None,
                        ),
                        comma=MaybeSentinel.DEFAULT,
                    ),
                ],
                lbracket=LeftSquareBracket(
                    whitespace_after=SimpleWhitespace(
                        value="",
                    ),
                ),
                rbracket=RightSquareBracket(
                    whitespace_before=SimpleWhitespace(
                        value="",
                    ),
                ),
                lpar=[],
                rpar=[],
                whitespace_after_value=SimpleWhitespace(
                    value="",
                ),
            ),
            whitespace_before_indicator=SimpleWhitespace(
                value="",
            ),
            whitespace_after_indicator=SimpleWhitespace(
                value=" ",
            ),
        )

    def register_import(self, import_: Import | ImportFrom):
        if isinstance(import_, ImportFrom):
            import_path, _, imported_elements = (
                Module([import_])
                .code.replace("from ", "", 1)
                .partition(" import ")
            )
            if import_path == self.config.interface_import_path:
                self.imported_interfaces.update(
                    set(imported_elements.split(", ")).difference({"Any"})
                )

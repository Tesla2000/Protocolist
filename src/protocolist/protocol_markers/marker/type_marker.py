from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Optional

from libcst import Annotation
from libcst import Import
from libcst import ImportFrom
from libcst import ImportStar
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
from mypy.memprofile import defaultdict

from ...annotation2string import annotation2string
from ...config import Config
from ...protocol_dict import ProtocolDict
from ...protocol_markers.mark_options import MarkOption
from ...to_camelcase import to_camelcase


class TypeMarker(ABC):
    type: MarkOption
    saved_annotations: dict[str, Optional[str]] = {}

    def __init__(self, config: Config):
        self.config = config
        self.imported_interfaces = set()
        self.imports = defaultdict(set)

    @abstractmethod
    def conv_parameter(
        self, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> "Param":
        pass

    def _create_literal_annotation(
        self, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> Optional[Annotation]:
        param_name = to_camelcase(updated_node.name.value)
        if param_name.lower() == "self":
            return
        protocols[param_name] += 1
        numeric_param_name = param_name + str(protocols[param_name])
        annotations[numeric_param_name] = None
        if self.config.keep_hints:
            self.saved_annotations[numeric_param_name] = annotation2string(
                updated_node.annotation
            )
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
                                value=f"'{numeric_param_name}'",
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
            import_path, *_ = (
                Module([import_])
                .code.replace("from ", "", 1)
                .partition(" import ")
            )
            self.imports[import_path].update(
                {"*"}
                if isinstance(import_.names, ImportStar)
                else set(
                    import_alias.evaluated_name
                    for import_alias in import_.names
                )
            )
            if import_path == self.config.interface_import_path:
                self.imported_interfaces.update(
                    self.imports[import_path].difference({"Any"})
                )

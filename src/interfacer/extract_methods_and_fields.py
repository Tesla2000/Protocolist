from __future__ import annotations

import re


def extract_methods_and_fields(code: str) -> tuple[set[str], set[str]]:
    return set(re.findall(r"    def [^\(]+\([^\)]+\):", code)), set(
        filter(
            lambda line: re.findall(r"^    \w+\:", line),
            code.splitlines(),
        )
    )


def extract_method_names_and_field_names(
    code: str,
) -> tuple[set[str], set[str]]:
    return set(re.findall(r"    def [^\(]+\([^\)]+\):", code)), set(
        filter(
            lambda line: re.findall(r"^    \w+\:", line),
            code.splitlines(),
        )
    )

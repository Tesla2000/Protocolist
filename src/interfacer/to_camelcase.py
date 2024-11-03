import re


def to_camelcase(text: str):
    underscores = re.findall(r"_\w", text)
    for underscore in underscores:
        text = text.replace(underscore, underscore[-1])
    return text[0].upper() + text[1:]
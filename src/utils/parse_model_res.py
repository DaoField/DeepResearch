# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
import re
from functools import lru_cache


@lru_cache(maxsize=128)
def _compile_xml_tag_regex(tag: str) -> re.Pattern:
    """Cache compiled regex patterns for XML tag extraction to avoid recompilation on each call."""
    return re.compile(rf'<{tag}>(.*?)</{tag}>', re.DOTALL | re.IGNORECASE)


def extract_xml_content(xml_str: str, tag: str) -> list[str]:
    """
    Extract content from strings containing<xml>tags

    Parameters:
        xml_str: A string containing<xml>tags
        tag: Tags in XML
    return:
        If the content within the tag is not found, return None
    """
    pattern = _compile_xml_tag_regex(tag)
    matches = pattern.findall(xml_str)
    if matches:
        return [match.strip() for match in matches]
    return None


if __name__ == '__main__':
    print(extract_xml_content(xml_str='<xml>test1</xml>\n<xml>test2</xml>', tag='xml'))

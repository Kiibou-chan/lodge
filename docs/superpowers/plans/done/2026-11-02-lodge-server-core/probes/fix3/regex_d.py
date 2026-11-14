"""Python's regular-expression \\d on str against str.isdecimal, over every code point."""

import re
import sys
import unicodedata

d = re.compile(r"\d")
matched = {c for c in range(0x110000) if d.fullmatch(chr(c))}
decimal = {c for c in range(0x110000) if chr(c).isdecimal()}
print(sys.version.split()[0], unicodedata.unidata_version, len(matched), len(decimal), matched == decimal)

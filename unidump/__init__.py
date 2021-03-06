#!/usr/bin/env python3
"""
hexdump(1) for Unicode data
"""


from typing import IO

from unidump.output import sanitize_char, print_line, fill_and_print
from unidump.env import Env


VERSION = '1.1.3'


def unidump(inbytes: IO[bytes], env: Env) -> None:
    """take a list of bytes and print their Unicode codepoints

    >>> import io
    >>> import sys
    >>> from unidump.env import Env
    >>> _env = Env(linelength=4, output=sys.stdout)
    >>> unidump(io.BytesIO(b'\\x01\\xF0\\x9F\\x99\\xB8ABC'), _env)
          0    0001 1F678 0041 0042    .\U0001F678AB
          7    0043                   C
    >>> unidump(io.BytesIO(b'\\xD7'), _env)
          0    ?D7?                   X
    >>> _env.encoding = 'latin1'
    >>> unidump(io.BytesIO(b'\\xD7'), _env)
          0    00D7                   \u00D7
    """

    byteoffset = 0
    bytebuffer = b''
    current_line = [0, [], '']

    byte = inbytes.read(1)
    while byte:
        byteoffset += 1
        bytebuffer += byte

        try:
            char = bytebuffer.decode(env.encoding)
        except UnicodeDecodeError:
            next_byte = inbytes.read(1)
            if not next_byte or len(bytebuffer) >= 4:
                for i, data in enumerate(bytebuffer):
                    current_line = (
                        fill_and_print(current_line, byteoffset - 4 + i,
                                       '?{:02X}?'.format(data), 'X', env)
                    )
                bytebuffer = b''
            byte = next_byte
            continue
        else:
            current_line = (
                fill_and_print(current_line, byteoffset - len(bytebuffer),
                               '{:04X}'.format(ord(char)), sanitize_char(char),
                               env)
            )

        bytebuffer = b''
        byte = inbytes.read(1)

    print_line(current_line, env)

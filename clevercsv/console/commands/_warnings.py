# -*- coding: utf-8 -*-

"""
List of common warnings
"""

import textwrap

WARNINGS = {
    "unicodedecodeerror": textwrap.fill(
        "A decoding error occurred while reading the file.\nThis usually "
        "means that the file encoding was detected incorrectly.\nYou can set "
        "this manually by using the <info>--encoding</info> flag."
    )
}

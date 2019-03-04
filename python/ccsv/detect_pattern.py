# -*- coding: utf-8 -*-

"""
Code for computing the pattern score.

Author: Gertjan van den Burg

"""

from __future__ import division

import collections

DEFAULT_EPS_PAT = 1e-3


def pattern_score(data, dialect, eps=DEFAULT_EPS_PAT):
    """
    Compute the pattern score for given data and a dialect.

    Parameters
    ----------

    data : string
        The data of the file as a raw character string

    dialect: dialect.Dialect
        The dialect object

    Returns
    -------
    score : float
        the pattern score

    """
    A = make_abstraction(data, dialect)
    row_patterns = collections.Counter(A.split("R"))
    P = 0
    for pat_k, Nk in row_patterns.items():
        Lk = len(pat_k.split("D"))
        P += Nk * (max(eps, Lk - 1) / Lk)
    P /= len(row_patterns)
    return P


def make_abstraction(data, dialect):
    """
    Create an abstract representation of the CSV file based on the dialect.

    """
    A = make_base_abstraction(data, dialect)
    A = merge_with_quotechar(A, dialect)
    A = fill_empties(A)
    A = strip_trailing(A)
    return A


def make_base_abstraction(S, dialect):
    """
    Create the basic form of the abstraction of the CSV file. This function 
    creates a stack and understands quotes, quote escaping with double quotes, 
    and escape chars.
    """
    stack = ""
    escape_next = False
    for s in S:
        if s in ["\r", "\n"]:
            if not stack.endswith("R"):
                stack += "R"
        elif s == dialect.delimiter:
            if escape_next:
                stack += "C"
                escape_next = False
            else:
                stack += "D"
        elif s == dialect.quotechar:
            if escape_next:
                stack += "C"
                escape_next = False
            else:
                stack += "Q"
        elif s == dialect.escapechar:
            if escape_next:
                if not stack.endswith("C"):
                    stack += "C"
                escape_next = False
            else:
                escape_next = True
        else:
            if escape_next:
                escape_next = False
            if not stack.endswith("C"):
                stack += "C"
    return stack


def merge_with_quotechar(S, dialect):
    """
    Merge quoted blocks (``QC...CQ``) to a single cell (``C``).
    """
    in_quotes = False
    i = 0
    quote_pairs = []
    while i < len(S):
        s = S[i]
        if not s == "Q":
            i += 1
            continue

        if not in_quotes:
            in_quotes = True
            begin_quotes = i
        else:
            if i + 1 < len(S) and S[i + 1] == "Q":
                i += 1
            else:
                end_quotes = i
                quote_pairs.append((begin_quotes, end_quotes))
                in_quotes = False
        i += 1

    # replace quoted blocks by C
    Sl = list(S)
    for begin, end in quote_pairs:
        for i in range(begin, end + 1):
            Sl[i] = "C"
    S = "".join(Sl)
    return S


def fill_empties(abstract):
    """
    Fill "empty cells" by inserting a cell character (C).
    """
    while "DD" in abstract:
        abstract = abstract.replace("DD", "DCD")

    while "DR" in abstract:
        abstract = abstract.replace("DR", "DCR")

    while "RD" in abstract:
        abstract = abstract.replace("RD", "RCD")

    while "CC" in abstract:
        abstract = abstract.replace("CC", "C")

    if abstract.startswith("D"):
        abstract = "C" + abstract

    if abstract.endswith("D"):
        abstract += "C"

    return abstract


def strip_trailing(abstract):
    """
    Strip trailing row separator from abstraction
    """
    while abstract.endswith("R"):
        abstract = abstract[:-1]
    return abstract
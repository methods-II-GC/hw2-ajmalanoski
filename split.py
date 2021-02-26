#!/usr/bin/env python
"""Splits the data into train, dev, and test sets."""

import argparse
import random

from typing import Iterator, IO, List


def read_tags(path: str) -> Iterator[List[List[str]]]:
    """
    Iterates over a file in multi-column tabular format, one sentence at a
    time.
    """
    with open(path, "r") as source:
        lines = []
        for line in source:
            line = line.rstrip()
            if line:
                lines.append(line.split())
            # A blank line. Indicates the end of the current sentence.
            else:
                yield lines.copy()
                lines.clear()
    # Just in case someone forgets to put a blank line at the end...
    if lines:
        yield lines


def write_tags(wf: IO, tags: List[List[str]]) -> None:
    for line in tags:
        line = " ".join(line)
        print(line, file=wf)
    print("", file=wf)


def main(args: argparse.Namespace) -> None:
    length = 0
    with open(args.input, 'r') as rf:
        for line in rf:
            # We count sentences by counting blank lines.
            if not line.strip():
                length += 1
    train_cutoff = round(length * 0.8)
    dev_cutoff = round(length * 0.1)
    test_cutoff = dev_cutoff
    train_size = 0
    dev_size = 0
    test_size = 0
    with open(args.train, 'w') as tf, open(args.dev, 'w') as df:
        with open(args.test, 'w') as ef:
            for sentence in read_tags(args.input):
                # 0 for train, 1 for dev, 2 for test
                write_to = random.choice(range(3))
                if write_to == 0:
                    if train_size < train_cutoff:
                        write_tags(tf, sentence)
                        train_size += 1
                    else:
                        write_to = 1
                if write_to == 1:
                    if dev_size < dev_cutoff:
                        write_tags(df, sentence)
                        dev_size += 1
                    else:
                        write_to = 2
                if write_to == 2:
                    if test_size < test_cutoff:
                        write_tags(ef, sentence)
                        test_size += 1
                    elif train_size < train_cutoff:
                        write_tags(tf, sentence)
                        train_size += 1
                    elif dev_size < dev_cutoff:
                        write_tags(df, sentence)
                        dev_size += 1
                    else:
                        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("train")
    parser.add_argument("dev")
    parser.add_argument("test")
    main(parser.parse_args())
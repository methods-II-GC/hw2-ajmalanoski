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
        word = " ".join(line)
        print(word, file=wf)
    print("", file=wf)


def main(args: argparse.Namespace) -> None:
    # Asserts to make sure that the values for the split make sense
    assert (
        0 < args.train_size and args.train_size < 1
    ), "train_size must be between 0 and 1"
    assert (
        0 < args.dev_size and args.dev_size < 1
    ), "dev_size must be between 0 and 1"
    assert (
        0 < args.test_size and args.test_size < 1
    ), "test_size must be between 0 and 1"
    random.seed(args.seed)
    corpus = list(read_tags(args.input))
    length = len(corpus)
    # Figure out cutoffs (as indices of `corpus`) for the training,
    # development, and test files.
    train_cutoff = round(length * args.train_size)
    dev_cutoff = train_cutoff + round(length * args.dev_size)
    test_cutoff = dev_cutoff + round(length * args.test_size)
    random.shuffle(corpus)
    with open(args.train, "w") as tf, open(args.dev, "w") as df:
        with open(args.test, "w") as ef:
            for i, sentence in enumerate(corpus):
                if i < train_cutoff:
                    write_tags(tf, sentence)
                elif i < dev_cutoff:
                    write_tags(df, sentence)
                elif i < test_cutoff:
                    write_tags(ef, sentence)
                else:
                    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="file to split")
    parser.add_argument("train", help="destination for training data")
    parser.add_argument("dev", help="destination for development data")
    parser.add_argument("test", help="destination for test data")
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        required=True,
        help="seed for random number generator",
    )
    parser.add_argument(
        "-t",
        "--train_size",
        type=float,
        default=0.8,
        help="proportion (not percent) of data for training",
    )
    parser.add_argument(
        "-d",
        "--dev_size",
        type=float,
        default=0.1,
        help="proportion (not percent) of data for development",
    )
    parser.add_argument(
        "-e",
        "--test_size",
        type=float,
        default=0.1,
        help="proportion (not percent) of data for testing",
    )
    main(parser.parse_args())

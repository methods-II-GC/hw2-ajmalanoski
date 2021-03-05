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
    length = 0
    with open(args.input, "r") as rf:
        for line in rf:
            # We count sentences by counting blank lines.
            if not line.strip():
                length += 1
    train_cutoff = round(length * args.train_size)
    dev_cutoff = round(length * args.dev_size)
    test_cutoff = round(length * args.test_size)
    with open(args.train, "w") as tf, open(args.dev, "w") as df:
        with open(args.test, "w") as ef:
            # Dictionary mapping files to a list containing (i) the current
            # number of sentences written the file and (ii) the total number
            # of sentences to be written to the file.
            counts = {
                tf: [0, train_cutoff],
                df: [0, dev_cutoff],
                ef: [0, test_cutoff],
            }
            weights = {
                tf: args.train_size,
                df: args.dev_size,
                ef: args.test_size,
            }
            outs = [tf, df, ef]
            for sentence in read_tags(args.input):
                wf = random.choices(
                    outs, weights=[weights[file] for file in outs]
                )[0]
                write_tags(wf, sentence)
                counts[wf][0] += 1  # Increase count by one
                # If `wf` has reached its quota for sentences, then remove
                # `wf` from `outs` so that we no longer write to it.
                if counts[wf][0] >= counts[wf][1]:
                    outs.remove(wf)
                # If there is no file left in `outs` to write to, then we are
                # done.
                if not outs:
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

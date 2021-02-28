#!/usr/bin/env python
"""Splits the data into train, dev, and test sets."""

import argparse
import random

from typing import Iterator, IO, List, Tuple, Union


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


def write_sentence(
    outs: List[Tuple[IO, int, int]], sentence: List[List[str]]
) -> int:
    """
    Args:
    outs: List of tuples, each consisting of a file, the count of entries
        written to that file, and the cutoff for that file.
    sentence: A sentence as a list of lists of tags, each list of tags being
        a word

    Returns the index of the file that was written to, or -1 if all the files
    are "full."
    """
    if not outs:
        return -1
    index = random.choice(range(len(outs)))
    if outs[index][1] < outs[index][2]:
        write_tags(outs[index][0], sentence)
        return index
    else:
        others = outs.copy()
        del others[index]
        return write_sentence(others, sentence)


def write_tags(wf: IO, tags: List[List[str]]) -> None:
    for line in tags:
        word = " ".join(line)
        print(word, file=wf)
    print("", file=wf)


def main(args: argparse.Namespace) -> None:
    random.seed(args.seed)
    length = 0
    with open(args.input, "r") as rf:
        for line in rf:
            # We count sentences by counting blank lines.
            if not line.strip():
                length += 1
    train_cutoff = round(length * 0.8)
    dev_cutoff = round(length * 0.1)
    test_cutoff = dev_cutoff
    with open(args.train, "w") as tf, open(args.dev, "w") as df:
        with open(args.test, "w") as ef:
            # List of filestreams, the count of sentences written to them so
            # far, and the maximum number of sentences to write to them.
            outs: List[Tuple[IO, int, int]] = [
                (tf, 0, train_cutoff),
                (df, 0, dev_cutoff),
                (ef, 0, test_cutoff),
            ]
            for sentence in read_tags(args.input):
                index = write_sentence(outs, sentence)
                if index >= 0:
                    outs[index] = (
                        outs[index][0],
                        outs[index][1] + 1,
                        outs[index][2],
                    )
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
    main(parser.parse_args())
